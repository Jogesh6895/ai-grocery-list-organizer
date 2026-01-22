import pytest
import os
from pathlib import Path
from unittest.mock import patch
from src.config import Config
from src.file_handler import FileHandler
from src.categorizer import GroceryCategorizer


@pytest.fixture
def integration_config(tmp_path):
    """Create a config for integration testing with temporary directories"""
    os.chdir(tmp_path)
    config = Config(
        model_name="test-model",
        input_dir=str(tmp_path / "input_data"),
        output_dir=str(tmp_path / "output_data"),
        max_retries=2,
        timeout=30,
        log_level="INFO",
    )
    config.ensure_directories()
    return config


@pytest.fixture
def sample_grocery_list():
    """Sample grocery list for testing"""
    return """Apples
Milk
Chicken Breast
Bread
Carrots
Orange Juice
Cheese
Bananas"""


class TestEndToEndCategorization:
    @patch("src.categorizer.ollama.generate")
    def test_complete_workflow_file_to_output(
        self, mock_generate, integration_config, sample_grocery_list
    ):
        """Test complete workflow from reading input file to writing categorized output"""
        # Setup mock response
        mock_response = {
            "response": """**Produce**
• Apples
• Bananas
• Carrots

**Dairy**
• Cheese
• Milk

**Meat**
• Chicken Breast

**Bakery**
• Bread

**Beverages**
• Orange Juice"""
        }
        mock_generate.return_value = mock_response

        # Create input file
        file_handler = FileHandler(integration_config)
        input_file = "grocery_list.txt"
        input_path = Path(integration_config.input_dir) / input_file
        with open(input_path, "w") as f:
            f.write(sample_grocery_list)

        # Read input
        items_text = file_handler.read_input_file(input_file)
        assert items_text == sample_grocery_list

        # Categorize
        categorizer = GroceryCategorizer(integration_config)
        result = categorizer.categorize(items_text)

        # Verify categorization
        assert result.success is True
        assert result.categorized_list is not None
        assert "Produce" in result.categorized_list.raw_response
        assert "Dairy" in result.categorized_list.raw_response

        # Write output
        output_file = "categorized_list.txt"
        output_path = file_handler.write_output_file(
            output_file, result.categorized_list.raw_response
        )

        # Verify output file exists and contains expected content
        assert output_path.exists()
        with open(output_path, "r") as f:
            content = f.read()
        assert "Produce" in content
        assert "Apples" in content
        assert "Dairy" in content

    @patch("src.categorizer.ollama.generate")
    def test_empty_input_file(self, mock_generate, integration_config):
        """Test handling of empty input file"""
        file_handler = FileHandler(integration_config)

        # Create empty input file
        input_file = "empty_list.txt"
        input_path = Path(integration_config.input_dir) / input_file
        with open(input_path, "w") as f:
            f.write("")

        # Read and categorize
        items_text = file_handler.read_input_file(input_file)
        categorizer = GroceryCategorizer(integration_config)
        result = categorizer.categorize(items_text)

        # Should fail due to empty input
        assert result.success is False
        assert "No items provided" in result.error_message


class TestBatchProcessingWorkflow:
    @patch("src.categorizer.ollama.generate")
    def test_batch_process_multiple_files(
        self, mock_generate, integration_config
    ):
        """Test batch processing of multiple grocery list files"""
        mock_response = {"response": "**Produce**\n• Apples\n**Dairy**\n• Milk"}
        mock_generate.return_value = mock_response

        file_handler = FileHandler(integration_config)
        categorizer = GroceryCategorizer(integration_config)

        # Create multiple input files
        test_files = {
            "list1.txt": "Apples\nMilk",
            "list2.txt": "Bananas\nCheese",
            "list3.txt": "Carrots\nYogurt",
        }

        for filename, content in test_files.items():
            input_path = Path(integration_config.input_dir) / filename
            with open(input_path, "w") as f:
                f.write(content)

        # Process all files
        input_files = file_handler.list_input_files("*.txt")
        assert len(input_files) == 3

        results = []
        for input_file in input_files:
            items_text = file_handler.read_input_file(input_file.name)
            result = categorizer.categorize(items_text)

            if result.success and result.categorized_list:
                output_filename = f"{input_file.stem}_categorized{input_file.suffix}"
                output_path = file_handler.write_output_file(
                    output_filename, result.categorized_list.raw_response
                )
                results.append((result, output_path))

        # Verify all files were processed successfully
        assert len(results) == 3
        assert all(r[0].success for r in results)
        assert all(r[1].exists() for r in results)

    @patch("src.categorizer.ollama.generate")
    def test_mixed_success_failure_batch(
        self, mock_generate, integration_config
    ):
        """Test batch processing with some files failing"""
        # First call succeeds, second call fails
        mock_generate.side_effect = [
            {"response": "**Produce**\n• Apples"},
            Exception("Model error"),
            {"response": "**Dairy**\n• Milk"},
        ]

        file_handler = FileHandler(integration_config)
        categorizer = GroceryCategorizer(integration_config)

        # Create test files
        test_files = ["list1.txt", "list2.txt", "list3.txt"]
        for filename in test_files:
            input_path = Path(integration_config.input_dir) / filename
            with open(input_path, "w") as f:
                f.write("Test item")

        # Process files
        results = []
        for filename in test_files:
            items_text = file_handler.read_input_file(filename)
            result = categorizer.categorize(items_text)
            results.append(result)

        # Verify mixed results
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True


class TestErrorRecovery:
    def test_file_not_found_error_recovery(
        self, integration_config
    ):
        """Test system handles missing input file gracefully"""
        file_handler = FileHandler(integration_config)

        with pytest.raises(FileNotFoundError):
            file_handler.read_input_file("nonexistent.txt")

    @patch("src.categorizer.ollama.generate")
    def test_categorization_retry_on_failure(
        self, mock_generate, integration_config
    ):
        """Test retry mechanism on categorization failure"""
        # First attempt fails, second succeeds
        mock_generate.side_effect = [
            Exception("Connection error"),
            {"response": "**Produce**\n• Apples"},
        ]

        categorizer = GroceryCategorizer(integration_config)
        result = categorizer.categorize("Apples\nMilk")

        # Should succeed after retry
        assert result.success is True
        assert mock_generate.call_count == 2

    @patch("src.categorizer.ollama.generate")
    def test_all_retries_exhausted(
        self, mock_generate, integration_config
    ):
        """Test behavior when all retry attempts are exhausted"""
        # All attempts fail
        mock_generate.side_effect = Exception("Persistent error")

        categorizer = GroceryCategorizer(integration_config)
        result = categorizer.categorize("Apples\nMilk")

        # Should fail after max retries
        assert result.success is False
        assert "Failed after" in result.error_message
        assert mock_generate.call_count == integration_config.max_retries


class TestDataFlowIntegration:
    @patch("src.categorizer.ollama.generate")
    def test_config_changes_propagate(self, mock_generate, tmp_path):
        """Test that configuration changes propagate through the system"""
        mock_response = {"response": "**Produce**\n• Apples"}
        mock_generate.return_value = mock_response

        # Create config with custom directories
        custom_input = str(tmp_path / "custom_input")
        custom_output = str(tmp_path / "custom_output")

        config = Config(
            model_name="custom-model",
            input_dir=custom_input,
            output_dir=custom_output,
            max_retries=1,
            timeout=15,
            log_level="DEBUG",
        )
        config.ensure_directories()

        # Verify directories were created as specified
        assert Path(custom_input).exists()
        assert Path(custom_output).exists()

        # Create input file in custom directory
        file_handler = FileHandler(config)
        input_path = Path(custom_input) / "test.txt"
        with open(input_path, "w") as f:
            f.write("Apples")

        # Process and verify output goes to custom directory
        items_text = file_handler.read_input_file("test.txt")
        categorizer = GroceryCategorizer(config)
        result = categorizer.categorize(items_text)

        output_path = file_handler.write_output_file(
            "output.txt", result.categorized_list.raw_response
        )

        assert output_path.parent == Path(custom_output)
        assert output_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

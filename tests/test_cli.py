import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.config import Config
from src.cli import (
    setup_logging,
    run_file_mode,
    run_batch_mode,
    run_interactive_mode,
    run_suggest_mode,
    main,
)
from src.models import ProcessingResult, CategorizedList


@pytest.fixture
def config():
    return Config(
        model_name="test-model",
        input_dir="input_data",
        output_dir="output_data",
        max_retries=2,
        timeout=30,
        log_level="INFO",
    )


@pytest.fixture
def temp_config(tmp_path):
    """Create a config with temporary directories"""
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


class TestSetupLogging:
    def test_setup_logging_info_level(self, caplog):
        """Test logging setup with INFO level"""
        import logging
        with caplog.at_level(logging.INFO):
            setup_logging("INFO")
        # Verify logging is configured (no exceptions raised)

    def test_setup_logging_debug_level(self, caplog):
        """Test logging setup with DEBUG level"""
        import logging
        with caplog.at_level(logging.DEBUG):
            setup_logging("DEBUG")
        # Verify logging is configured (no exceptions raised)


class TestRunFileMode:
    @patch("src.cli.GroceryCategorizer")
    @patch("src.cli.FileHandler")
    def test_run_file_mode_success(
        self, mock_file_handler_class, mock_categorizer_class, temp_config
    ):
        """Test successful file mode execution"""
        # Setup mocks
        mock_file_handler = MagicMock()
        mock_file_handler.read_input_file.return_value = (
            "Apples\nMilk\nBread"
        )
        mock_file_handler.write_output_file.return_value = (
            Path(temp_config.output_dir) / "output.txt"
        )
        mock_file_handler_class.return_value = mock_file_handler

        mock_categorizer = MagicMock()
        categorized_list = CategorizedList(raw_response="**Produce**\n• Apples")
        mock_categorizer.categorize.return_value = ProcessingResult(
            success=True, categorized_list=categorized_list
        )
        mock_categorizer_class.return_value = mock_categorizer

        # Execute
        result = run_file_mode(temp_config, "input.txt", "output.txt")

        # Verify
        assert result.success is True
        assert result.output_file is not None
        mock_file_handler.read_input_file.assert_called_once_with("input.txt")
        mock_file_handler.write_output_file.assert_called_once()

    @patch("src.cli.FileHandler")
    def test_run_file_mode_file_not_found(
        self, mock_file_handler_class, temp_config
    ):
        """Test file mode with non-existent file"""
        mock_file_handler = MagicMock()
        mock_file_handler.read_input_file.side_effect = FileNotFoundError("File not found")
        mock_file_handler_class.return_value = mock_file_handler

        result = run_file_mode(temp_config, "nonexistent.txt", "output.txt")

        assert result.success is False
        assert "File not found" in result.error_message


class TestRunBatchMode:
    @patch("src.cli.GroceryCategorizer")
    @patch("src.cli.FileHandler")
    def test_run_batch_mode_success(
        self, mock_file_handler_class, mock_categorizer_class, temp_config
    ):
        """Test batch mode with multiple files"""
        # Setup mocks
        mock_file_handler = MagicMock()
        input_files = [Path("file1.txt"), Path("file2.txt")]
        mock_file_handler.list_input_files.return_value = input_files
        mock_file_handler.read_input_file.return_value = "Apples\nMilk"
        mock_file_handler.write_output_file.return_value = (
            Path(temp_config.output_dir) / "out.txt"
        )
        mock_file_handler_class.return_value = mock_file_handler

        mock_categorizer = MagicMock()
        categorized_list = CategorizedList(raw_response="**Produce**\n• Apples")
        mock_categorizer.categorize.return_value = ProcessingResult(
            success=True, categorized_list=categorized_list
        )
        mock_categorizer_class.return_value = mock_categorizer

        # Execute
        results = run_batch_mode(temp_config, "*.txt")

        # Verify
        assert len(results) == 2
        assert all(r.success for r in results)

    @patch("src.cli.FileHandler")
    def test_run_batch_mode_no_files(self, mock_file_handler_class, temp_config):
        """Test batch mode with no matching files"""
        mock_file_handler = MagicMock()
        mock_file_handler.list_input_files.return_value = []
        mock_file_handler_class.return_value = mock_file_handler

        results = run_batch_mode(temp_config, "*.txt")

        assert len(results) == 0


class TestRunInteractiveMode:
    @patch("src.cli.GroceryCategorizer")
    @patch("src.cli.FileHandler")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_interactive_mode_with_items(
        self, mock_print, mock_input, mock_file_handler_class, mock_categorizer_class, temp_config
    ):
        """Test interactive mode with user input"""
        # Setup mocks
        mock_input.side_effect = ["Apples", "Milk", "DONE", "n"]

        mock_file_handler = MagicMock()
        mock_file_handler_class.return_value = mock_file_handler

        mock_categorizer = MagicMock()
        categorized_list = CategorizedList(
            raw_response="**Produce**\n• Apples\n**Dairy**\n• Milk"
        )
        mock_categorizer.categorize.return_value = ProcessingResult(
            success=True, categorized_list=categorized_list
        )
        mock_categorizer_class.return_value = mock_categorizer

        # Execute
        result = run_interactive_mode(temp_config)

        # Verify
        assert result.success is True
        assert result.categorized_list is not None

    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_interactive_mode_no_items(
        self, mock_print, mock_input, temp_config
    ):
        """Test interactive mode when user enters no items"""
        mock_input.side_effect = ["DONE"]

        result = run_interactive_mode(temp_config)

        assert result.success is False
        assert "No items were entered" in result.error_message


class TestRunSuggestMode:
    @patch("src.cli.GroceryCategorizer")
    @patch("src.cli.FileHandler")
    def test_run_suggest_mode_success(
        self, mock_file_handler_class, mock_categorizer_class, temp_config
    ):
        """Test suggest mode successfully returns categories"""
        mock_file_handler = MagicMock()
        mock_file_handler.read_input_file.return_value = "Apples\nMilk\nChicken"
        mock_file_handler_class.return_value = mock_file_handler

        mock_categorizer = MagicMock()
        mock_categorizer.suggest_categories.return_value = [
            "Produce",
            "Dairy",
            "Meat",
        ]
        mock_categorizer_class.return_value = mock_categorizer

        categories = run_suggest_mode(temp_config, "input.txt")

        assert len(categories) == 3
        assert "Produce" in categories

    @patch("src.cli.FileHandler")
    def test_run_suggest_mode_file_error(
        self, mock_file_handler_class, temp_config
    ):
        """Test suggest mode with file error"""
        mock_file_handler = MagicMock()
        mock_file_handler.read_input_file.side_effect = FileNotFoundError("File not found")
        mock_file_handler_class.return_value = mock_file_handler

        categories = run_suggest_mode(temp_config, "nonexistent.txt")

        assert len(categories) == 0


class TestMain:
    @patch("src.cli.run_file_mode")
    @patch("src.cli.Config")
    def test_main_file_mode_success(self, mock_config_class, mock_run_file_mode):
        """Test main function in file mode"""
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config_class.from_env.return_value = mock_config

        result = ProcessingResult(success=True, output_file="output.txt")
        mock_run_file_mode.return_value = result

        with patch("sys.argv", ["cli.py", "--mode", "file", "--input", "test.txt"]):
            exit_code = main()

        assert exit_code == 0

    @patch("src.cli.Config")
    def test_main_file_mode_missing_input(
        self, mock_config_class
    ):
        """Test main function with missing input argument"""
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config_class.from_env.return_value = mock_config

        with patch("sys.argv", ["cli.py", "--mode", "file"]):
            exit_code = main()

        assert exit_code == 1

    @patch("src.cli.run_batch_mode")
    @patch("src.cli.Config")
    def test_main_batch_mode(self, mock_config_class, mock_run_batch_mode):
        """Test main function in batch mode"""
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config_class.from_env.return_value = mock_config

        results = [
            ProcessingResult(success=True),
            ProcessingResult(success=True),
        ]
        mock_run_batch_mode.return_value = results

        with patch("sys.argv", ["cli.py", "--mode", "batch"]):
            exit_code = main()

        assert exit_code == 0

    @patch("src.cli.run_interactive_mode")
    @patch("src.cli.Config")
    def test_main_interactive_mode(
        self, mock_config_class, mock_run_interactive_mode
    ):
        """Test main function in interactive mode"""
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config_class.from_env.return_value = mock_config

        result = ProcessingResult(success=True)
        mock_run_interactive_mode.return_value = result

        with patch("sys.argv", ["cli.py", "--mode", "interactive"]):
            exit_code = main()

        assert exit_code == 0

    @patch("src.cli.run_suggest_mode")
    @patch("src.cli.Config")
    @patch("builtins.print")
    def test_main_suggest_mode(
        self, mock_print, mock_config_class, mock_run_suggest_mode
    ):
        """Test main function in suggest mode"""
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config_class.from_env.return_value = mock_config

        categories = ["Produce", "Dairy", "Meat"]
        mock_run_suggest_mode.return_value = categories

        with patch(
            "sys.argv", ["cli.py", "--mode", "suggest", "--input", "test.txt"]
        ):
            exit_code = main()

        assert exit_code == 0

    @patch("src.cli.Config")
    def test_main_keyboard_interrupt(self, mock_config_class):
        """Test main function handles keyboard interrupt"""
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config.ensure_directories.side_effect = KeyboardInterrupt()
        mock_config_class.from_env.return_value = mock_config

        with patch("sys.argv", ["cli.py", "--mode", "file", "--input", "test.txt"]):
            exit_code = main()

        assert exit_code == 130


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

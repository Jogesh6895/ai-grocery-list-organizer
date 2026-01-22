import pytest
from unittest.mock import patch, MagicMock
from src.config import Config
from src.categorizer import GroceryCategorizer
from src.models import ProcessingResult


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
def categorizer(config):
    return GroceryCategorizer(config)


def test_categorizer_build_prompt(categorizer):
    items_text = "Apples\nMilk\nBread"
    prompt = categorizer._build_prompt(items_text)

    assert "Apples" in prompt
    assert "Milk" in prompt
    assert "categorize" in prompt.lower()
    assert "sort" in prompt.lower()
    assert "alphabetically" in prompt.lower()


def test_categorize_empty_items(categorizer):
    result = categorizer.categorize("")
    assert result.success is False
    assert "No items provided" in result.error_message


def test_categorize_whitespace_only(categorizer):
    result = categorizer.categorize("   \n   ")
    assert result.success is False


@patch("src.categorizer.ollama.generate")
def test_categorize_success(mock_generate, categorizer):
    mock_response = {
        "response": "**Produce**\n• Apples\n• Bananas\n\n**Dairy**\n• Milk\n• Cheese"
    }
    mock_generate.return_value = mock_response

    result = categorizer.categorize("Apples\nMilk\nBananas")

    assert result.success is True
    assert result.categorized_list is not None
    assert "Produce" in result.categorized_list.raw_response
    assert result.categorized_list.raw_response == mock_response["response"]


@patch("src.categorizer.ollama.generate")
def test_categorize_retry_on_failure(mock_generate, categorizer):
    mock_generate.side_effect = [Exception("Error"), Exception("Error")]

    result = categorizer.categorize("Apples\nMilk")

    assert result.success is False
    assert "Failed after" in result.error_message


@patch("src.categorizer.ollama.generate")
def test_categorize_single_item(mock_generate, categorizer):
    mock_response = {"response": "Produce"}
    mock_generate.return_value = mock_response

    category = categorizer.categorize_single_item("Apples")

    assert category == "Produce"
    mock_generate.assert_called_once()


@patch("src.categorizer.ollama.generate")
def test_categorize_single_item_failure(mock_generate, categorizer):
    mock_generate.side_effect = Exception("Error")

    category = categorizer.categorize_single_item("Apples")

    assert category == "Uncategorized"


@patch("src.categorizer.ollama.generate")
def test_suggest_categories(mock_generate, categorizer):
    mock_response = {"response": "Produce\nDairy\nMeat\nBakery\nBeverages"}
    mock_generate.return_value = mock_response

    categories = categorizer.suggest_categories("Apples\nMilk\nChicken")

    assert len(categories) == 5
    assert "Produce" in categories
    assert "Dairy" in categories
    assert "Meat" in categories


@patch("src.categorizer.ollama.generate")
def test_suggest_categories_failure(mock_generate, categorizer):
    mock_generate.side_effect = Exception("Error")

    categories = categorizer.suggest_categories("Apples\nMilk")

    # Returns default categories on failure (6 categories)
    assert len(categories) == 6
    assert "Produce" in categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import pytest
from src.models import GroceryItem, Category, CategorizedList, ProcessingResult


def test_grocery_item_creation():
    item = GroceryItem(name="Apples", quantity="2 lbs")
    assert item.name == "Apples"
    assert item.quantity == "2 lbs"


def test_grocery_item_optional_quantity():
    item = GroceryItem(name="Milk")
    assert item.name == "Milk"
    assert item.quantity is None


def test_category_creation():
    category = Category(name="Produce", items=["Apples", "Bananas"])
    assert category.name == "Produce"
    assert len(category.items) == 2
    assert "Apples" in category.items


def test_category_empty_items():
    category = Category(name="Dairy")
    assert category.name == "Dairy"
    assert category.items == []


def test_categorized_list_creation():
    categorized = CategorizedList()
    assert categorized.categories == {}
    assert categorized.raw_response is None


def test_categorized_list_add_category():
    categorized = CategorizedList()
    category = Category(name="Produce", items=["Apples"])
    categorized.add_category(category)
    assert "Produce" in categorized.categories
    assert categorized.get_items_by_category("Produce") == ["Apples"]


def test_categorized_list_get_all_categories():
    categorized = CategorizedList()
    categorized.add_category(Category(name="Produce"))
    categorized.add_category(Category(name="Dairy"))
    categories = categorized.get_all_categories()
    assert len(categories) == 2
    assert "Produce" in categories
    assert "Dairy" in categories


def test_processing_result_success():
    result = ProcessingResult(success=True, input_source="test.txt")
    assert result.success is True
    assert result.error_message is None
    assert result.input_source == "test.txt"


def test_processing_result_failure():
    result = ProcessingResult(success=False, error_message="File not found")
    assert result.success is False
    assert result.error_message == "File not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class GroceryItem:
    name: str
    quantity: Optional[str] = None


@dataclass
class Category:
    name: str
    items: List[str] = field(default_factory=list)


@dataclass
class CategorizedList:
    categories: Dict[str, Category] = field(default_factory=dict)
    raw_response: Optional[str] = None

    def add_category(self, category: Category) -> None:
        self.categories[category.name] = category

    def get_items_by_category(self, category_name: str) -> List[str]:
        if category_name in self.categories:
            return self.categories[category_name].items
        return []

    def get_all_categories(self) -> List[str]:
        return list(self.categories.keys())


@dataclass
class ProcessingResult:
    success: bool
    categorized_list: Optional[CategorizedList] = None
    error_message: Optional[str] = None
    input_source: Optional[str] = None
    output_file: Optional[str] = None

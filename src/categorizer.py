import logging
import ollama
from typing import Optional
from .config import Config
from .models import CategorizedList, ProcessingResult

logger = logging.getLogger(__name__)


class GroceryCategorizer:
    def __init__(self, config: Config):
        self.config = config

    def _build_prompt(self, items_text: str) -> str:
        return f"""You are an assistant that categorizes and sorts grocery items.

Here is a list of grocery items:

{items_text}

Please:

1. Categorize these items into appropriate categories such as Produce, Dairy, Meat, Bakery, Beverages, Pantry, Snacks, Household, etc.
2. Sort the items alphabetically within each category.
3. Present the categorized list in a clear and organized manner, using the following format:

**Category Name**
• Item 1
• Item 2
• Item 3

Return only the categorized list without any introductory or concluding text.
"""

    def categorize(self, items_text: str) -> ProcessingResult:
        if not items_text or not items_text.strip():
            return ProcessingResult(
                success=False, error_message="No items provided for categorization"
            )

        prompt = self._build_prompt(items_text)

        for attempt in range(self.config.max_retries):
            try:
                response = ollama.generate(model=self.config.model_name, prompt=prompt)
                generated_text = response.get("response", "").strip()

                categorized_list = CategorizedList(raw_response=generated_text)

                logger.info("Categorization completed successfully")

                return ProcessingResult(success=True, categorized_list=categorized_list)

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    return ProcessingResult(
                        success=False,
                        error_message=f"Failed after {self.config.max_retries} attempts: {str(e)}",
                    )

        return ProcessingResult(
            success=False,
            error_message="Unexpected error occurred during categorization",
        )

    def categorize_single_item(self, item: str) -> str:
        prompt = f"""Categorize the following grocery item into ONE appropriate category (Produce, Dairy, Meat, Bakery, Beverages, Pantry, Snacks, Household, Frozen, etc.):
Item: {item}

Return only the category name, nothing else."""

        try:
            response = ollama.generate(model=self.config.model_name, prompt=prompt)
            return response.get("response", "").strip()
        except Exception as e:
            logger.error(f"Failed to categorize item '{item}': {str(e)}")
            return "Uncategorized"

    def suggest_categories(self, items_text: str) -> list[str]:
        prompt = f"""Analyze the following grocery items and suggest the most appropriate categories for organizing them. Return only category names, one per line, without numbering or bullets:

{items_text}"""

        try:
            response = ollama.generate(model=self.config.model_name, prompt=prompt)
            categories_text = response.get("response", "").strip()
            return [cat.strip() for cat in categories_text.split("\n") if cat.strip()]
        except Exception as e:
            logger.error(f"Failed to suggest categories: {str(e)}")
            return ["Produce", "Dairy", "Meat", "Bakery", "Beverages", "Pantry"]

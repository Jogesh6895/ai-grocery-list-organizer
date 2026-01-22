import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime

from .config import Config
from .file_handler import FileHandler
from .categorizer import GroceryCategorizer
from .models import ProcessingResult


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def run_file_mode(
    config: Config, input_filename: str, output_filename: str
) -> ProcessingResult:
    file_handler = FileHandler(config)
    categorizer = GroceryCategorizer(config)

    try:
        items_text = file_handler.read_input_file(input_filename)
        result = categorizer.categorize(items_text)

        if result.success and result.categorized_list:
            raw_response = result.categorized_list.raw_response or ""
            output_path = file_handler.write_output_file(output_filename, raw_response)
            result.output_file = str(output_path)
            result.input_source = input_filename

        return result
    except Exception as e:
        logging.error(f"Error in file mode: {str(e)}")
        return ProcessingResult(success=False, error_message=str(e))


def run_batch_mode(config: Config, pattern: str = "*.txt") -> list[ProcessingResult]:
    file_handler = FileHandler(config)
    categorizer = GroceryCategorizer(config)

    results = []
    input_files = file_handler.list_input_files(pattern)

    if not input_files:
        logging.warning(f"No input files found matching pattern: {pattern}")
        return results

    logging.info(f"Found {len(input_files)} input files to process")

    for input_file in input_files:
        try:
            items_text = file_handler.read_input_file(input_file.name)
            result = categorizer.categorize(items_text)

            if result.success and result.categorized_list:
                output_filename = f"{input_file.stem}_categorized{input_file.suffix}"
                raw_response = result.categorized_list.raw_response or ""
                output_path = file_handler.write_output_file(
                    output_filename, raw_response
                )
                result.output_file = str(output_path)
                result.input_source = input_file.name

            results.append(result)
        except Exception as e:
            logging.error(f"Error processing file {input_file.name}: {str(e)}")
            results.append(
                ProcessingResult(
                    success=False, error_message=str(e), input_source=input_file.name
                )
            )

    return results


def run_interactive_mode(config: Config) -> ProcessingResult:
    file_handler = FileHandler(config)
    categorizer = GroceryCategorizer(config)

    print("=== Grocery Categorizer - Interactive Mode ===")
    print("Enter grocery items (one per line), or 'DONE' when finished:")

    items = []
    while True:
        item = input(f"Item {len(items) + 1}: ").strip()
        if item.upper() == "DONE":
            break
        if item:
            items.append(item)

    if not items:
        return ProcessingResult(success=False, error_message="No items were entered")

    items_text = "\n".join(items)
    result = categorizer.categorize(items_text)

    if result.success and result.categorized_list:
        print("\n=== Categorized List ===\n")
        print(result.categorized_list.raw_response)

        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == "y":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"categorized_list_{timestamp}.txt"
            raw_response = result.categorized_list.raw_response or ""
            output_path = file_handler.write_output_file(output_filename, raw_response)
            result.output_file = str(output_path)
            print(f"Saved to: {output_path}")

    return result


def run_suggest_mode(config: Config, input_filename: str) -> list[str]:
    file_handler = FileHandler(config)
    categorizer = GroceryCategorizer(config)

    try:
        items_text = file_handler.read_input_file(input_filename)
        categories = categorizer.suggest_categories(items_text)
        return categories if categories else []
    except Exception as e:
        logging.error(f"Error in suggest mode: {str(e)}")
        return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grocery Categorizer - Organize and categorize grocery items using AI"
    )
    parser.add_argument(
        "--mode",
        choices=["file", "batch", "interactive", "suggest"],
        default="file",
        help="Mode of operation",
    )
    parser.add_argument(
        "--input", "-i", help="Input file name (for file and suggest modes)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="categorized_grocery_list.txt",
        help="Output file name",
    )
    parser.add_argument(
        "--pattern", "-p", default="*.txt", help="File pattern for batch mode"
    )
    parser.add_argument(
        "--model", "-m", help="Ollama model name (overrides OLLAMA_MODEL env var)"
    )

    args = parser.parse_args()
    config = Config.from_env()

    if args.model:
        config.model_name = args.model

    setup_logging(config.log_level)
    config.ensure_directories()

    try:
        if args.mode == "file":
            if not args.input:
                logging.error("--input is required for file mode")
                return 1

            result = run_file_mode(config, args.input, args.output)

            if result.success:
                logging.info(f"Success! Output saved to: {result.output_file}")
                return 0
            else:
                logging.error(f"Failed: {result.error_message}")
                return 1

        elif args.mode == "batch":
            results = run_batch_mode(config, args.pattern)

            success_count = sum(1 for r in results if r.success)
            logging.info(
                f"Processed {len(results)} files: {success_count} succeeded, {len(results) - success_count} failed"
            )

            return 0 if success_count == len(results) else 1

        elif args.mode == "interactive":
            result = run_interactive_mode(config)
            return 0 if result.success else 1

        elif args.mode == "suggest":
            if not args.input:
                logging.error("--input is required for suggest mode")
                return 1

            categories = run_suggest_mode(config, args.input)

            if categories:
                print("\n=== Suggested Categories ===\n")
                for i, category in enumerate(categories, 1):
                    print(f"{i}. {category}")
                return 0
            else:
                logging.error("Failed to generate category suggestions")
                return 1

    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

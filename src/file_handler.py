import logging
from pathlib import Path
from typing import List, Optional
from .config import Config

logger = logging.getLogger(__name__)


class FileHandler:
    def __init__(self, config: Config):
        self.config = config

    def read_input_file(self, filename: str) -> str:
        filepath = self.config.get_input_path(filename)

        if not filepath.exists():
            raise FileNotFoundError(f"Input file '{filepath}' not found")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        logger.info(f"Successfully read input file: {filepath}")
        return content

    def write_output_file(self, filename: str, content: str) -> Path:
        self.config.ensure_directories()
        filepath = self.config.get_output_path(filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Successfully wrote output file: {filepath}")
        return filepath

    def list_input_files(self, pattern: str = "*") -> List[Path]:
        input_dir = Path(self.config.input_dir)

        if not input_dir.exists():
            logger.warning(f"Input directory '{input_dir}' does not exist")
            return []

        return sorted(input_dir.glob(pattern))

    def validate_input_file(self, filename: str) -> bool:
        filepath = self.config.get_input_path(filename)
        return filepath.exists() and filepath.is_file()

    def get_file_content_lines(self, filename: str) -> List[str]:
        content = self.read_input_file(filename)
        return [line.strip() for line in content.split("\n") if line.strip()]

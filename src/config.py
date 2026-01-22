import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class Config:
    model_name: str
    input_dir: str
    output_dir: str
    max_retries: int
    timeout: int
    log_level: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            model_name=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            input_dir=os.getenv("INPUT_DIR", "input_data"),
            output_dir=os.getenv("OUTPUT_DIR", "output_data"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            timeout=int(os.getenv("TIMEOUT", "60")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def get_input_path(self, filename: str) -> Path:
        return Path(self.input_dir) / filename

    def get_output_path(self, filename: str) -> Path:
        return Path(self.output_dir) / filename

    def ensure_directories(self) -> None:
        Path(self.input_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

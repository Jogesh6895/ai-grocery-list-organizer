import pytest
from pathlib import Path
from src.config import Config


def test_config_from_env():
    config = Config.from_env()
    assert config.model_name is not None
    assert config.input_dir == "input_data"
    assert config.output_dir == "output_data"
    assert config.max_retries == 3
    assert config.timeout == 60
    assert config.log_level == "INFO"


def test_config_get_paths():
    config = Config.from_env()
    input_path = config.get_input_path("test.txt")
    output_path = config.get_output_path("output.txt")
    assert str(input_path).endswith("input_data/test.txt")
    assert str(output_path).endswith("output_data/output.txt")


def test_config_ensure_directories(tmp_path):
    import os

    os.chdir(tmp_path)
    config = Config.from_env()
    config.ensure_directories()
    assert Path(config.input_dir).exists()
    assert Path(config.output_dir).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

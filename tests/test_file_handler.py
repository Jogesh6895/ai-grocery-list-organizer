import pytest
import os
from pathlib import Path
from src.config import Config
from src.file_handler import FileHandler


@pytest.fixture
def temp_config(tmp_path):
    os.chdir(tmp_path)
    config = Config.from_env()
    config.input_dir = str(tmp_path / "input_data")
    config.output_dir = str(tmp_path / "output_data")
    config.ensure_directories()
    return config


@pytest.fixture
def file_handler(temp_config):
    return FileHandler(temp_config)


def test_file_handler_write_read(file_handler, temp_config):
    content = "Apples\nMilk\nBread"
    output_file = file_handler.write_output_file("test.txt", content)
    assert output_file.exists()

    read_content = file_handler.read_input_file("test.txt")
    assert read_content == content


def test_file_handler_read_nonexistent(file_handler):
    with pytest.raises(FileNotFoundError):
        file_handler.read_input_file("nonexistent.txt")


def test_file_handler_get_file_content_lines(file_handler):
    content = "Apples\nMilk\nBread"
    file_handler.write_output_file("test.txt", content)
    lines = file_handler.get_file_content_lines("test.txt")
    assert lines == ["Apples", "Milk", "Bread"]


def test_file_handler_list_input_files(file_handler, temp_config):
    file_handler.write_output_file("test1.txt", "content1")
    file_handler.write_output_file("test2.txt", "content2")

    files = file_handler.list_input_files("*.txt")
    assert len(files) == 2


def test_file_handler_validate_input_file(file_handler, temp_config):
    file_handler.write_output_file("existing.txt", "content")

    assert file_handler.validate_input_file("existing.txt") is True
    assert file_handler.validate_input_file("nonexistent.txt") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

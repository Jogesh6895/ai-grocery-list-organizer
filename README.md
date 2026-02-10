# AI Grocery List Organizer

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-LLM-000000?logo=ollama)](https://ollama.ai/)
[![AI](https://img.shields.io/badge/AI-Powered-purple)]()
[![Privacy](https://img.shields.io/badge/Privacy-Local%20Processing-brightgreen)]()
[![CLI](https://img.shields.io/badge/CLI-Tool-orange)](https://en.wikipedia.org/wiki/Command-line_interface)
[![Tests](https://img.shields.io/badge/Tests-pytest-success)](https://docs.pytest.org/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen)](#-contributing)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-blueviolet)](AGENTS.md)

AI-powered grocery categorization tool that automatically organizes shopping lists into intelligent categories using local LLM models. Perfect for organized shopping.

## Features

- **Multiple Operation Modes**:
  - `file` - Process grocery lists from input files
  - `batch` - Process multiple input files at once
  - `interactive` - Enter items interactively through the command line
  - `suggest` - Get category suggestions for your grocery items

- **Configurable**:
  - Custom Ollama models
  - Environment-based configuration
  - Flexible input/output directories

- **Secure**:
  - No hardcoded credentials
  - Environment variable support
  - Local processing via Ollama

## Prerequisites

- Python 3.9+
- Ollama installed and running
- An Ollama model pulled (default: `llama3.2:3b`)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai_grocery_list_organizer
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure Ollama is installed and running:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2:3b
```

## Configuration

Set environment variables (optional):

```bash
export OLLAMA_MODEL="llama3.2:3b"
export INPUT_DIR="input_data"
export OUTPUT_DIR="output_data"
export MAX_RETRIES="3"
export TIMEOUT="60"
export LOG_LEVEL="INFO"
```

## Usage

### File Mode

Process a single grocery list file:

```bash
python -m src.cli --mode file --input grocery_list.txt --output categorized_list.txt
```

### Batch Mode

Process all text files in the input directory:

```bash
python -m src.cli --mode batch --pattern "*.txt"
```

### Interactive Mode

Enter grocery items interactively:

```bash
python -m src.cli --mode interactive
```

### Suggest Mode

Get category suggestions for items in a file:

```bash
python -m src.cli --mode suggest --input grocery_list.txt
```

### Using a Different Model

Override the default model:

```bash
python -m src.cli --mode file --input grocery_list.txt --model llama3.2:1b
```

## Directory Structure

```
ai_grocery_list_organizer/
├── src/
│   ├── __init__.py
│   ├── cli.py           # Command-line interface
│   ├── config.py        # Configuration management
│   ├── models.py        # Data models
│   ├── file_handler.py  # File I/O operations
│   └── categorizer.py   # Core categorization logic
├── input_data/          # Place input files here
├── output_data/         # Categorized files are saved here
├── tests/
│   └── fixtures/        # Test data
├── .gitignore
├── LICENSE              # MIT License
├── requirements.txt
├── README.md
├── AGENTS.md
└── TEST_REPORT.md
```

## Input Format

Place your grocery list files in the `input_data/` directory with one item per line:

```
Apples
Chicken Breast
Milk
Bread
Carrots
Orange Juice
```

## Output Format

Categorized lists are saved to the `output_data/` directory:

```
**Produce**
• Apples
• Bananas
• Carrots

**Dairy**
• Milk
• Cheese
• Yogurt

**Meat**
• Chicken Breast
• Ground Beef
```

## Testing

This project includes comprehensive unit and integration tests to ensure code quality and correctness.

### Running Tests

Run all tests:

```bash
pytest tests/ -v
```

Run tests with coverage report:

```bash
pytest --cov=src --cov-report=term-missing tests/
```

Generate HTML coverage report:

```bash
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in your browser
```

Run specific test modules:

```bash
pytest tests/test_categorizer.py -v
pytest tests/test_cli.py -v
pytest tests/test_integration.py -v
```

### Test Coverage

The test suite includes 50 total test cases across 6 test modules:

- **Unit Tests**: Test individual components in isolation (42 tests)
  - `test_models.py` (9 tests) - Data model tests
  - `test_config.py` (3 tests) - Configuration management tests
  - `test_file_handler.py` (5 tests) - File I/O operation tests
  - `test_categorizer.py` (9 tests) - Core categorization logic tests
  - `test_cli.py` (16 tests) - Command-line interface tests

- **Integration Tests**: Test complete workflows (8 tests)
  - `test_integration.py` (8 tests) - End-to-end workflow tests

Target coverage: **≥85%**

## Troubleshooting

### Ollama connection issues

Ensure Ollama is running:

```bash
ollama serve
```

### Model not found

Pull the required model:

```bash
ollama pull llama3.2:3b
```

### Input file not found

Ensure your input files are in the `input_data/` directory.

## Contributing

Please see `AGENTS.md` for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

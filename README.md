# Grocery Categorizer

An AI-powered grocery categorization tool that organizes and sorts grocery items into appropriate categories using local LLM models via Ollama.

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
cd new_implementation
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
new_implementation/
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
├── requirements.txt
├── README.md
└── AGENTS.md
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

The test suite includes:

- **Unit Tests**: Test individual components in isolation
  - `test_models.py` - Data model tests
  - `test_config.py` - Configuration management tests
  - `test_file_handler.py` - File I/O operation tests
  - `test_categorizer.py` - Core categorization logic tests
  - `test_cli.py` - Command-line interface tests

- **Integration Tests**: Test complete workflows
  - `test_integration.py` - End-to-end workflow tests

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

MIT License

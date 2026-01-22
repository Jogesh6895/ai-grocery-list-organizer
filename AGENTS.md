# AGENTS.md - Contributing Guidelines

## Project Overview

This document provides guidelines for AI agents and developers contributing to the AI Grocery List Organizer project.

## Code Style Guidelines

### General Principles

- Keep code modular and focused on single responsibilities
- Use type hints for function parameters and return values
- Write descriptive function and variable names
- Keep functions concise and focused
- Document complex logic with clear comments

### Module Structure

The project follows a modular architecture:

```
src/
├── config.py         - Configuration management
├── models.py         - Data models (dataclasses)
├── file_handler.py   - File I/O operations
├── categorizer.py    - Core business logic
├── cli.py            - Command-line interface
└── __init__.py       - Package exports
```

## When Adding Features

### 1. Understand the existing patterns

Before making changes, review the existing code to understand:
- How configuration is managed (environment variables, defaults)
- How errors are handled (try-except, logging, result objects)
- How data flows through the modules

### 2. Follow the established patterns

Use `ProcessingResult` for operations that can fail:
```python
from .models import ProcessingResult

def some_operation() -> ProcessingResult:
    try:
        return ProcessingResult(success=True, ...)
    except Exception as e:
        return ProcessingResult(success=False, error_message=str(e))
```

Use `Config.from_env()` for configuration:
```python
config = Config.from_env()
config.ensure_directories()
```

### 3. Maintain backward compatibility

- Don't remove or change function signatures without deprecation
- Add new optional parameters to existing functions
- Use environment variables for configuration

## Testing Guidelines

### Unit Tests

- Test each module in isolation
- Mock external dependencies (Ollama API, file system)
- Test both success and failure cases
- Use descriptive test names

### Integration Tests

- Test module interactions
- Test with real input files
- Verify output format

## Security Considerations

### Never expose secrets

- No hardcoded API keys, tokens, or credentials
- Use environment variables for all sensitive data
- Ensure `.gitignore` excludes files with secrets
- Never commit `.env` files

### Input Validation

- Validate all user inputs
- Sanitize file paths to prevent path traversal
- Handle unexpected input gracefully

## Logging Guidelines

- Use appropriate log levels: DEBUG, INFO, WARNING, ERROR
- Include context in log messages
- Don't log sensitive information
- Use structured logging where possible

## Documentation Guidelines

### Code Comments

- Add comments for non-obvious logic
- Keep comments up to date with code changes
- Avoid redundant comments

### README Updates

When adding features, update:
- Installation instructions (if new dependencies)
- Usage examples
- Configuration options

## Common Patterns

### Error Handling

```python
try:
    result = some_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {str(e)}")
    return ProcessingResult(success=False, error_message=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return ProcessingResult(success=False, error_message=str(e))
```

### File Operations

```python
from .file_handler import FileHandler

file_handler = FileHandler(config)
content = file_handler.read_input_file(filename)
file_handler.write_output_file(filename, content)
```

### Categorization

```python
from .categorizer import GroceryCategorizer

categorizer = GroceryCategorizer(config)
result = categorizer.categorize(items_text)
if result.success:
    print(result.categorized_list.raw_response)
```

## Code Review Checklist

Before submitting changes:

- [ ] Code follows existing patterns
- [ ] Type hints are present and correct
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] No hardcoded secrets
- [ ] Comments explain complex logic
- [ ] Tests are included (if applicable)
- [ ] README is updated (if needed)

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_categorizer.py

# Run with coverage
pytest --cov=src tests/
```

## Questions or Issues

If you encounter issues or have questions:
1. Review the codebase for similar patterns
2. Check the README for usage information
3. Examine existing tests for examples
4. Follow the established conventions even if not explicitly documented

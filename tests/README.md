# Test Suite for HardPotato

This directory contains the pytest test suite for the hardpotato library.

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_potentiostat.py
```

## Test Structure

- `conftest.py` - Shared pytest fixtures
- `test_potentiostat.py` - Tests for the main potentiostat module
- `test_emstatpico.py` - Tests for EmStat Pico functionality
- `test_load_data.py` - Tests for data loading
- `test_save_data.py` - Tests for data saving

## Mocking

Tests use mocking to avoid requiring actual hardware connections.
Serial communication and subprocess calls are mocked in the fixtures.

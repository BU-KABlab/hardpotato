# HardPotato Tests

This directory contains unit tests for the HardPotato library using pytest.

## Running the Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest test_potentiostat.py
```

To run tests with verbose output:

```bash
pytest -v
```

To run tests with coverage information:

```bash
pytest --cov=hardpotato
```

## Test Structure

- `conftest.py`: Contains fixtures used across multiple test files
- `test_potentiostat.py`: Tests for the main potentiostat module
- `test_emstatpico.py`: Tests for the EmStat Pico-specific functionality
- `test_pico_mscript.py`: Tests for parsing EmStat Pico script results
- `test_pico_serial.py`: Tests for serial communication with EmStat Pico
- `test_pico_instrument.py`: Tests for the EmStat Pico instrument interface
- `test_save_data.py`: Tests for data saving functionality
- `test_load_data.py`: Tests for data loading functionality

## Adding New Tests

When adding new tests, follow these patterns:

1. Use fixtures from `conftest.py` wherever possible
2. Mock hardware communication
3. Test both success and failure cases
4. Check returned values carefully

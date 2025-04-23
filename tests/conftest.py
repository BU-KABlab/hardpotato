import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.fixture
def temp_folder():
    """Create a temporary folder for test data."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def mock_serial():
    """Mock the serial port communication."""
    with patch("hardpotato.pico_serial.Serial") as mock_serial:
        mock_instance = MagicMock()
        mock_serial.return_value.__enter__.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for CHI potentiostats."""
    with patch("subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def sample_cv_data():
    """Generate sample CV data."""
    E = np.linspace(-0.5, 0.5, 100)
    i = 1e-6 * (E**3 - E)  # Simple cubic function to mimic CV curve
    return {"E": E, "i": i}


@pytest.fixture
def sample_ca_data():
    """Generate sample CA data."""
    t = np.linspace(0, 1, 100)
    i = 1e-6 * np.exp(-5 * t)  # Exponential decay for CA
    return {"t": t, "i": i}


@pytest.fixture
def sample_ocp_data():
    """Generate sample OCP data."""
    t = np.linspace(0, 2, 100)
    E = 0.2 + 0.05 * np.exp(-t)  # Exponential approach to equilibrium
    return {"t": t, "E": E}


@pytest.fixture
def sample_emstatpico_result():
    """Generate sample EmStat Pico result lines."""
    lines = [
        "P\r",
        "NM\r",
        "aa 0.000000\r",
        "ab 0.200000\r",
        "ba 0.000020\r",
        "aa 0.010000\r",
        "ab 0.200000\r",
        "ba 0.000019\r",
        "aa 0.020000\r",
        "ab 0.200000\r",
        "ba 0.000018\r",
        "*\r",
    ]
    return lines


@pytest.fixture
def mock_instrument():
    """Mock EmStat Pico instrument."""
    with patch("hardpotato.pico_instrument.Instrument") as mock_inst:
        instance = MagicMock()
        mock_inst.return_value = instance
        yield instance

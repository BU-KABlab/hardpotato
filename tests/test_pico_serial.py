from unittest.mock import MagicMock, patch

import pytest

import hardpotato.pico_serial as serial


@pytest.mark.parametrize(
    "vid_pid,expected",
    [
        ([(0x10C4, 0xEA60)], True),  # CP210x USB to UART Bridge
        ([(0x0000, 0x0000)], False),  # Unknown device
    ],
)
def test_is_cp210x(vid_pid, expected):
    """Test CP210x detection."""
    result = serial.is_cp210x(vid_pid)
    assert result == expected


@patch("serial.tools.list_ports.comports")
def test_auto_detect_port_found(mock_comports):
    """Test auto-detection when a port is found."""
    mock_port = MagicMock()
    mock_port.vid = 0x10C4
    mock_port.pid = 0xEA60
    mock_port.device = "/dev/ttyUSB0"
    mock_comports.return_value = [mock_port]

    port = serial.auto_detect_port()

    assert port == "/dev/ttyUSB0"


@patch("serial.tools.list_ports.comports")
def test_auto_detect_port_not_found(mock_comports):
    """Test auto-detection when no port is found."""
    mock_port = MagicMock()
    mock_port.vid = 0x0000
    mock_port.pid = 0x0000
    mock_port.device = "/dev/ttyUSB0"
    mock_comports.return_value = [mock_port]

    with pytest.raises(RuntimeError):
        serial.auto_detect_port()


def test_serial_init():
    """Test Serial object initialization."""
    with patch("serial.Serial") as mock_serial:
        mock_instance = MagicMock()
        mock_serial.return_value = mock_instance

        ser = serial.Serial("/dev/ttyUSB0", 1)

        mock_serial.assert_called_once_with("/dev/ttyUSB0", 230400, timeout=1)


def test_serial_context_manager():
    """Test Serial context manager."""
    with patch("serial.Serial"):
        with patch.object(serial.Serial, "__enter__") as mock_enter:
            with patch.object(serial.Serial, "__exit__") as mock_exit:
                mock_enter.return_value = "mocked serial"

                with serial.Serial("/dev/ttyUSB0", 1) as s:
                    assert s == "mocked serial"

                mock_enter.assert_called_once()
                mock_exit.assert_called_once()

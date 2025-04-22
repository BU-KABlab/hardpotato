from unittest.mock import MagicMock, call, patch

import hardpotato.pico_instrument as instrument


def test_instrument_init():
    """Test Instrument initialization."""
    mock_comm = MagicMock()
    inst = instrument.Instrument(mock_comm)
    assert inst.comm == mock_comm


def test_send_cmd():
    """Test sending command."""
    mock_comm = MagicMock()
    inst = instrument.Instrument(mock_comm)
    inst.write("test command")
    mock_comm.write.assert_called_once_with(b"test command")


def test_read_line():
    """Test reading line."""
    mock_comm = MagicMock()
    mock_comm.readline.return_value = b"test response\r\n"
    inst = instrument.Instrument(mock_comm)
    response = inst.readline()
    assert response == "test response\r\n"
    mock_comm.readline.assert_called_once()


def test_readlines_until_end():
    """Test reading lines until end marker."""
    mock_comm = MagicMock()
    mock_comm.readline.side_effect = [b"line1\n", b"line2\n", b"*\n", b"\n"]
    inst = instrument.Instrument(mock_comm)

    lines = inst.readlines_until_end()

    assert lines == ["line1\n", "line2\n", "*\n"]
    assert mock_comm.readline.call_count == 4


def test_read_version():
    """Test reading version."""
    mock_comm = MagicMock()
    mock_comm.readline.side_effect = [b"tespico\n", b"*\n"]
    inst = instrument.Instrument(mock_comm)

    version = inst.get_firmware_version()

    assert version == "espico *"
    mock_comm.write.assert_called_once_with(b"t\n")
    assert mock_comm.readline.call_count == 2


def test_send_script_from_string():
    """Test sending script from string."""
    mock_comm = MagicMock()
    script = ["line1", "line2", "line3"]
    inst = instrument.Instrument(mock_comm)

    with patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.readlines.return_value = script

        inst.send_script("test_script.mscr")

        assert mock_comm.write.call_count >= 3
        mock_comm.write.assert_has_calls(
            [call(b"line1"), call(b"line2"), call(b"line3")], any_order=False
        )

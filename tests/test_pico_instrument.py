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
    inst.send_cmd("test command")
    mock_comm.write.assert_called_once_with(b"test command\n")


def test_read_line():
    """Test reading line."""
    mock_comm = MagicMock()
    mock_comm.readline.return_value = b"test response\r\n"
    inst = instrument.Instrument(mock_comm)
    response = inst.read_line()
    assert response == "test response\r"
    mock_comm.readline.assert_called_once()


def test_read_until():
    """Test reading until specific response."""
    mock_comm = MagicMock()
    mock_comm.readline.side_effect = [b"line1\r\n", b"line2\r\n", b"endmarker\r\n"]
    inst = instrument.Instrument(mock_comm)

    lines = list(inst.read_until("endmarker"))

    assert lines == ["line1\r", "line2\r", "endmarker\r"]
    assert mock_comm.readline.call_count == 3


def test_readlines_until_end():
    """Test reading lines until end marker."""
    mock_comm = MagicMock()
    mock_comm.readline.side_effect = [b"line1\r\n", b"line2\r\n", b"*\r\n"]
    inst = instrument.Instrument(mock_comm)

    lines = inst.readlines_until_end()

    assert lines == ["line1\r", "line2\r", "*\r"]
    assert mock_comm.readline.call_count == 3


def test_read_version():
    """Test reading version."""
    mock_comm = MagicMock()
    mock_comm.readline.side_effect = [b"t\r\n", b"* t\r\n"]
    inst = instrument.Instrument(mock_comm)

    version = inst.read_version()

    assert version == "t"
    mock_comm.write.assert_called_once_with(b"t\n")
    assert mock_comm.readline.call_count == 2


def test_send_script_from_string():
    """Test sending script from string."""
    mock_comm = MagicMock()
    script = "line1\nline2\nline3\n"
    inst = instrument.Instrument(mock_comm)

    with patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = script

        inst.send_script("test_script.mscr")

        assert mock_comm.write.call_count >= 3
        mock_comm.write.assert_has_calls(
            [call(b"line1\n"), call(b"line2\n"), call(b"line3\n")], any_order=False
        )


@patch("time.sleep")
def test_await_response(mock_sleep):
    """Test awaiting response."""
    mock_comm = MagicMock()
    mock_comm.readline.side_effect = [b"", b"", b"response\r\n"]
    inst = instrument.Instrument(mock_comm)

    response = inst.await_response(max_tries=5)

    assert response == "response\r"
    assert mock_comm.readline.call_count == 3
    assert mock_sleep.call_count == 2

import numpy as np

import hardpotato.pico_mscript as mscript


def test_parse_metadata():
    """Test parsing metadata from result line."""
    line = "M 37 2097152 20000 2000 0"
    metadata = mscript.parse_metadata(line)

    assert metadata["npoints"] == 37
    assert metadata["current_range"] == 2097152
    assert metadata["e_range"] == 20000
    assert metadata["max_buffer_index"] == 2000
    assert metadata["status"] == 0


def test_parse_var():
    """Test parsing variable line."""
    line = "aa 0.123456"
    var_id, value = mscript.parse_var(line)

    assert var_id == "aa"
    assert value == 0.123456


def test_parse_result_lines():
    """Test parsing full result lines."""
    lines = [
        "P\r",
        "NM\r",
        "M 5 2097152 20000 2000 0\r",
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

    result = mscript.parse_result_lines(lines)

    assert len(result) == 3  # 3 data points
    assert "aa" in result.dtype.names  # Check column exists
    assert "ab" in result.dtype.names
    assert "ba" in result.dtype.names
    assert result["aa"][0] == 0.0
    assert result["aa"][1] == 0.01
    assert result["aa"][2] == 0.02
    assert result["ba"][0] == 0.000020
    assert result["ba"][1] == 0.000019
    assert result["ba"][2] == 0.000018


def test_get_column_data_default():
    """Test getting column data with default column names."""
    # Create a structured array mimicking parse_result_lines output
    dtype = [("aa", float), ("ab", float), ("ba", float)]
    data = np.array(
        [(0.0, 0.2, 0.000020), (0.01, 0.2, 0.000019), (0.02, 0.2, 0.000018)],
        dtype=dtype,
    )

    t, E, i = mscript.get_column_data(data)

    assert np.array_equal(t, np.array([0.0, 0.01, 0.02]))
    assert np.array_equal(E, np.array([0.2, 0.2, 0.2]))
    assert np.array_equal(i, np.array([0.000020, 0.000019, 0.000018]))


def test_get_column_data_custom():
    """Test getting column data with custom column names."""
    # Create a structured array with different column names
    dtype = [("ac", float), ("ad", float), ("bb", float)]
    data = np.array(
        [(0.0, 0.2, 0.000020), (0.01, 0.2, 0.000019), (0.02, 0.2, 0.000018)],
        dtype=dtype,
    )

    t, E, i = mscript.get_column_data(data, t_col="ac", E_col="ad", i_col="bb")

    assert np.array_equal(t, np.array([0.0, 0.01, 0.02]))
    assert np.array_equal(E, np.array([0.2, 0.2, 0.2]))
    assert np.array_equal(i, np.array([0.000020, 0.000019, 0.000018]))

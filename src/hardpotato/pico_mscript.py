"""
PalmSens MethodSCRIPT module

This module provides functionality to translate and interpret the output of a
MethodSCRIPT (the measurement data).

The most relevant functions are:
  - parse_mscript_data_package(line)
  - parse_result_lines(lines)
  - get_values_by_column(curves, column, icurve=None)

For example, to extract data from EmStat Pico measurements:
  1. Get raw lines from the device using pico_instrument.Instrument.readlines_until_end()
  2. Parse the lines using parse_result_lines()
  3. Extract specific data (time, potential, current) using get_values_by_column()

-------------------------------------------------------------------------------
Copyright (c) 2021 PalmSens BV
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   - Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
   - Neither the name of PalmSens BV nor the names of its contributors
     may be used to endorse or promote products derived from this software
     without specific prior written permission.
   - This license does not release you from any requirement to obtain separate
          licenses from 3rd party patent holders to use this software.
   - Use of the software either in source or binary form must be connected to,
          run on or loaded to an PalmSens BV component.

DISCLAIMER: THIS SOFTWARE IS PROVIDED BY PALMSENS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Standard library imports
import collections
import math
import warnings
from typing import Dict, List, Optional

# Third-party imports
import numpy as np

# Custom types
VarType = collections.namedtuple("VarType", ["id", "name", "unit"])
MScriptVar = collections.namedtuple(
    "MScriptVar", ["type", "value", "value_string", "metadata"]
)

# Dictionary for the conversion of the SI prefixes.
SI_PREFIX_FACTOR = {
    # supported SI prefixes:
    "a": 1e-18,  # atto
    "f": 1e-15,  # femto
    "p": 1e-12,  # pico
    "n": 1e-9,  # nano
    "u": 1e-6,  # micro
    "m": 1e-3,  # milli
    " ": 1e0,
    "k": 1e3,  # kilo
    "M": 1e6,  # mega
    "G": 1e9,  # giga
    "T": 1e12,  # tera
    "P": 1e15,  # peta
    "E": 1e18,  # exa
    # special case:
    "i": 1e0,  # integer
}

# List of MethodSCRIPT variable types.
MSCRIPT_VAR_TYPES_LIST = [
    VarType("aa", "unknown", ""),
    VarType("ab", "WE vs RE potential", "V"),
    VarType("ac", "CE vs GND potential", "V"),
    VarType("ad", "SE vs GND potential", "V"),
    VarType("ae", "RE vs GND potential", "V"),
    VarType("af", "WE vs GND potential", "V"),
    VarType("ag", "WE vs CE potential", "V"),
    VarType("as", "AIN0 potential", "V"),
    VarType("at", "AIN1 potential", "V"),
    VarType("au", "AIN2 potential", "V"),
    VarType("av", "AIN3 potential", "V"),
    VarType("aw", "AIN4 potential", "V"),
    VarType("ax", "AIN5 potential", "V"),
    VarType("ay", "AIN6 potential", "V"),
    VarType("az", "AIN7 potential", "V"),
    VarType("ba", "WE current", "A"),
    VarType("ca", "Phase", "degrees"),
    VarType("cb", "Impedance", "\u2126"),  # NB: '\u2126' = ohm symbol
    VarType("cc", "Z_real", "\u2126"),
    VarType("cd", "Z_imag", "\u2126"),
    VarType("ce", "EIS E TDD", "V"),
    VarType("cf", "EIS I TDD", "A"),
    VarType("cg", "EIS sampling frequency", "Hz"),
    VarType("ch", "EIS E AC", "Vrms"),
    VarType("ci", "EIS E DC", "V"),
    VarType("cj", "EIS I AC", "Arms"),
    VarType("ck", "EIS I DC", "A"),
    VarType("da", "Applied potential", "V"),
    VarType("db", "Applied current", "A"),
    VarType("dc", "Applied frequency", "Hz"),
    VarType("dd", "Applied AC amplitude", "Vrms"),
    VarType("ea", "Channel", ""),
    VarType("eb", "Time", "s"),
    VarType("ec", "Pin mask", ""),
    VarType("ed", "Temperature", "\u00b0 Celsius"),  # NB: '\u00B0' = degrees symbol
    VarType("ha", "Generic current 1", "A"),
    VarType("hb", "Generic current 2", "A"),
    VarType("hc", "Generic current 3", "A"),
    VarType("hd", "Generic current 4", "A"),
    VarType("ia", "Generic potential 1", "V"),
    VarType("ib", "Generic potential 2", "V"),
    VarType("ic", "Generic potential 3", "V"),
    VarType("id", "Generic potential 4", "V"),
    VarType("ja", "Misc. generic 1", ""),
    VarType("jb", "Misc. generic 2", ""),
    VarType("jc", "Misc. generic 3", ""),
    VarType("jd", "Misc. generic 4", ""),
]

MSCRIPT_VAR_TYPES_DICT = {x.id: x for x in MSCRIPT_VAR_TYPES_LIST}

METADATA_STATUS_FLAGS = [
    (0x1, "TIMING_ERROR"),
    (0x2, "OVERLOAD"),
    (0x4, "UNDERLOAD"),
    (0x8, "OVERLOAD_WARNING"),
]

MSCRIPT_CURRENT_RANGES_EMSTAT_PICO = {
    0: "100 nA",
    1: "2 uA",
    2: "4 uA",
    3: "8 uA",
    4: "16 uA",
    5: "32 uA",
    6: "63 uA",
    7: "125 uA",
    8: "250 uA",
    9: "500 uA",
    10: "1 mA",
    11: "5 mA",
    128: "100 nA (High speed)",
    129: "1 uA (High speed)",
    130: "6 uA (High speed)",
    131: "13 uA (High speed)",
    132: "25 uA (High speed)",
    133: "50 uA (High speed)",
    134: "100 uA (High speed)",
    135: "200 uA (High speed)",
    136: "1 mA (High speed)",
    137: "5 mA (High speed)",
}

MSCRIPT_CURRENT_RANGES_EMSTAT4 = {
    # EmStat4 LR only:
    3: "1 nA",
    6: "10 nA",
    # EmStat4 LR/HR:
    9: "100 nA",
    12: "1 uA",
    15: "10 uA",
    18: "100 uA",
    21: "1 mA",
    24: "10 mA",
    # EmStat4 HR only:
    27: "100 mA",
}

MSCRIPT_POTENTIAL_RANGES_EMSTAT4 = {
    2: "50 mV",
    3: "100 mV",
    4: "200 mV",
    5: "500 mV",
    6: "1 V",
}


def get_variable_type(id: str) -> VarType:
    """Get the variable type with the specified id.

    Args:
        id: Two-letter string identifier for the variable type.

    Returns:
        A VarType namedtuple containing id, name, and unit.
        If the id is not recognized, returns a generic VarType with "unknown" name.

    Example:
        >>> var_type = get_variable_type("ba")
        >>> print(f"{var_type.name} ({var_type.unit})")
        WE current (A)
    """
    if id in MSCRIPT_VAR_TYPES_DICT:
        return MSCRIPT_VAR_TYPES_DICT[id]
    warnings.warn('Unsupported VarType id "%s"!' % id)
    return VarType(id, "unknown", "")


def metadata_status_to_text(status: int) -> str:
    """Convert a metadata status value to a human-readable string.

    Args:
        status: Integer status value from metadata.

    Returns:
        A string describing the status flags that are set, or "OK" if no flags are set.
    """
    descriptions = []
    for mask, description in METADATA_STATUS_FLAGS:
        if status & mask:
            descriptions.append(description)
    if descriptions:
        return " | ".join(descriptions)
    else:
        return "OK"


def metadata_current_range_to_text(device_type: str, var_type: VarType, cr: int) -> str:
    """Convert a current range value to a human-readable string.

    Args:
        device_type: The device type string (e.g., "EmStat Pico").
        var_type: The variable type (VarType namedtuple).
        cr: The current range value from metadata.

    Returns:
        A string representation of the current range (e.g., "100 nA").
    """
    cr_text = None
    if device_type == "EmStat Pico":
        cr_text = MSCRIPT_CURRENT_RANGES_EMSTAT_PICO.get(cr)
    elif "EmStat4" in device_type:
        # For EmStat4 series instruments, the range can be a current range or
        # potential range, depending on the variable type.
        if var_type.id in ["ab", "cd"]:
            cr_text = MSCRIPT_POTENTIAL_RANGES_EMSTAT4.get(cr)
        else:
            cr_text = MSCRIPT_CURRENT_RANGES_EMSTAT4.get(cr)
    return cr_text or "UNKNOWN CURRENT RANGE"


class MScriptVar:
    """Class to store and parse a received MethodSCRIPT variable.

    This class handles the parsing and interpretation of individual
    variables received from a PalmSens potentiostat during a measurement.

    Attributes:
        id: Two-letter string identifier for the variable type.
        raw_value: The decoded integer value from the data package.
        si_prefix: The SI prefix character (e.g., 'n' for nano).
        raw_metadata: List of raw metadata tokens.
        metadata: Parsed metadata dictionary.
        type: VarType namedtuple containing id, name, and unit.
        value: Actual value with SI prefix applied.
        value_string: Human-readable string representing the value with units.
    """

    def __init__(self, data: str):
        """Initialize from a MethodSCRIPT variable string.

        Args:
            data: The variable data string from a data package.
        """
        assert len(data) >= 10
        self.data = data[:]
        # Parse the variable type.
        self.id = data[0:2]
        # Check for NaN.
        if data[2:10] == "     nan":
            self.raw_value = math.nan
            self.si_prefix = " "
        else:
            # Parse the (raw) value,
            self.raw_value = self.decode_value(data[2:9])
            # Store the SI prefix.
            self.si_prefix = data[9]
        # Store the (raw) metadata.
        self.raw_metadata = data.split(",")[1:]
        # Parse the metadata.
        self.metadata = self.parse_metadata(self.raw_metadata)

    def __repr__(self) -> str:
        """Return a string representation for debugging."""
        return "MScriptVar(%r)" % self.data

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return self.value_string

    @property
    def type(self) -> VarType:
        """Get the variable type."""
        return get_variable_type(self.id)

    @property
    def si_prefix_factor(self) -> float:
        """Get the multiplication factor for the SI prefix."""
        return SI_PREFIX_FACTOR[self.si_prefix]

    @property
    def value(self) -> float:
        """Get the actual value with SI prefix applied."""
        return self.raw_value * self.si_prefix_factor

    @property
    def value_string(self) -> str:
        """Get a human-readable string representation of the value with units."""
        if self.type.unit:
            if self.si_prefix_factor == 1:
                if math.isnan(self.value):
                    return "NaN %s" % (self.type.unit)
                else:
                    return "%d %s" % (self.raw_value, self.type.unit)
            else:
                return "%d %s%s" % (self.raw_value, self.si_prefix, self.type.unit)
        else:
            return "%.9g" % (self.value)

    @staticmethod
    def decode_value(var: str) -> int:
        """Decode the raw value of a MethodSCRIPT variable in a data package.

        The input is a 7-digit hexadecimal string (without the variable type
        and/or SI prefix). The output is the converted (signed) integer value.

        Args:
            var: 7-character hexadecimal string.

        Returns:
            Decoded signed integer value.
        """
        assert len(var) == 7
        # Convert the 7 hexadecimal digits to an integer value and
        # subtract the offset.
        return int(var, 16) - (2**27)

    @staticmethod
    def parse_metadata(tokens: List[str]) -> Dict[str, int]:
        """Parse the (optional) metadata.

        Args:
            tokens: List of metadata tokens.

        Returns:
            Dictionary of parsed metadata with keys:
                - "status": Status flags
                - "cr": Current range
        """
        metadata = {}
        for token in tokens:
            if (len(token) == 2) and (token[0] == "1"):
                value = int(token[1], 16)
                metadata["status"] = value
            if (len(token) == 3) and (token[0] == "2"):
                value = int(token[1:], 16)
                metadata["cr"] = value
        return metadata


def parse_mscript_data_package(line: str) -> Optional[List[MScriptVar]]:
    """Parse a MethodSCRIPT data package.

    The format of a MethodSCRIPT data package is described in the
    MethodSCRIPT documentation. It starts with a 'P' and ends with a
    '\n' character. A package consists of an arbitrary number of
    variables. Each variable consists of a type (describing the
    variable), a value, and optionally one or more metadata values.

    Args:
        line: A line of text received from the potentiostat.

    Returns:
        A list of variables (of type `MScriptVar`) if the line is a valid
        data package, or None if the line is not a data package.

    Example:
        >>> line = "Peb0000001 ;ba2000000n,10,20a\n"
        >>> vars = parse_mscript_data_package(line)
        >>> print(f"Time: {vars[0].value} s, Current: {vars[1].value} A")
        Time: 1.0 s, Current: 2.0e-9 A
    """
    if line.startswith("P") and line.endswith("\n"):
        return [MScriptVar(var) for var in line[1:-1].split(";")]
    return None


def parse_result_lines(lines: List[str]) -> List[List[List[MScriptVar]]]:
    """Parse the result of a MethodSCRIPT and return a list of curves.

    This method returns a list of curves, where each curve is a list of
    measurement data (packages) seperated by an end-of-curve terminator
    such as '*', '+' or '-'. Each data package is a list of variables of
    type MScriptVar.

    Args:
        lines: List of lines received from the potentiostat.

    Returns:
        A list of curves, where each curve is a list of data packages,
        and each data package is a list of variables.

    Note:
        The return type is a list of list of list of MScriptVars, and
        each variable can be accessed as `result[curve][row][col]`. For
        example, `result[1][2][3]` is the 4th variable of the 3th data point
        of the 2nd measurement loop.

    Example:
        >>> lines = ["Peb0000001 ;ba2000000n\n", "*\n"]
        >>> curves = parse_result_lines(lines)
        >>> print(f"Time: {curves[0][0][0].value} s")
        Time: 1.0 s
    """
    curves = []
    current_curve = []
    for line in lines:
        # NOTE:
        # '+' = end of loop
        # '*' = end of measurement loop
        # '-' = end of scan, within measurement loop, in case nscans(>1)
        if line and line[0] in "+*-":
            # End of scan or (measurement) loop detected.
            # Store curve if not empty.
            if current_curve:
                curves.append(current_curve)
                current_curve = []
        else:
            # No end of scan. Try to parse as data package.
            package = parse_mscript_data_package(line)
            if package:
                # Line was a valid package.
                # Append the package to the current curve.
                current_curve.append(package)
    return curves


def get_values_by_column(
    curves: List[List[List[MScriptVar]]], column: int, icurve: Optional[int] = None
) -> np.ndarray:
    """Get all values from the specified column.

    This function extracts values from specific variables in the data packages
    and returns them as a numpy array for easy processing and plotting.

    Args:
        curves: A list of curves as returned by parse_result_lines().
        column: Which variable to extract (index within each data package).
        icurve: Which curve to use. If None (default), data from all curves
                are concatenated.

    Returns:
        A numpy array containing the values of each variable in the specified column.

    Example:
        ```python
        # Parse data from a measurement
        curves = parse_result_lines(data_lines)

        # Extract time, potential, and current
        time = get_values_by_column(curves, 0)       # First column (time)
        potential = get_values_by_column(curves, 1)   # Second column (potential)
        current = get_values_by_column(curves, 2)     # Third column (current)

        # Plot data
        import matplotlib.pyplot as plt
        plt.plot(potential, current)
        plt.xlabel('Potential (V)')
        plt.ylabel('Current (A)')
        plt.show()
        ```
    """
    if icurve is None:
        values = []
        for curve in curves:
            values.extend(row[column].value for row in curve)
    else:
        values = [row[column].value for row in curves[icurve]]
    return np.asarray(values)

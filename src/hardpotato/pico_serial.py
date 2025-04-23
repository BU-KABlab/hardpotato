"""
PalmSens Serial Port (UART) interface

This module implements the serial interface to the PalmSens instrument.

This module uses the "pyserial" module, which must be installed before running
this code. See https://pypi.org/project/pyserial/ for more information.

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
import logging
from typing import Any

# Third-party imports
import serial
import serial.tools.list_ports

LOG = logging.getLogger(__name__)


def _is_mscript_device(port: serial.tools.list_ports_common.ListPortInfo) -> bool:
    """Check if the specified port is a known MethodSCRIPT device.

    Args:
        port: Serial port information object from pyserial.

    Returns:
        bool: True if the port is likely a MethodSCRIPT device, False otherwise.

    Note:
        This is an internal function used by auto_detect_port().
    """
    # NOTES:
    # - Since the EmStat Pico uses a generic FTDI USB-to-Serial chip,
    #   it is identified by Windows as "USB Serial Port". This is the
    #   text to look for when using the auto detection feature. Note
    #   that an EmStat Pico or Sensit BT cannot be auto-detected if
    #   there are also other devices connected that use this name.
    # - An EmStat4 device in bootloader mode would be identified as
    #   'EmStat4 Bootloader', but we only want to connect to devices
    #   that can run MethodSCRIPTs, so we do not include that here.
    return (
        port.description == "EmStat4"
        or port.description.startswith("ESPicoDev")
        or port.description.startswith("SensitBT")
        or port.description.startswith("SensitSmart")
        or
        # ^ Above names are used in Linux
        # v Below names are used in Windows
        port.description.startswith("EmStat4 LR (COM")
        or port.description.startswith("EmStat4 HR (COM")
        or port.description.startswith("MultiEmStat4 LR (COM")
        or port.description.startswith("MultiEmStat4 HR (COM")
        or port.description.startswith("USB Serial Port")
    )


def auto_detect_port() -> str:
    """Auto-detect the serial communication port for an EmStat device.

    This function searches for an available port connected to a supported
    PalmSens device. If exactly one port matches the criteria, that port's
    name will be returned. If there are either no matches or multiple matches,
    an exception is raised.

    Returns:
        str: The name of the detected port (e.g., 'COM3' on Windows).

    Raises:
        Exception: If auto-detection fails because no matching ports are found
                  or because multiple matching ports are found.

    Example:
        ```python
        try:
            port = auto_detect_port()
            print(f"Found PalmSens device on port: {port}")
        except Exception as e:
            print(f"Auto-detection failed: {e}")
            port = 'COM3'  # Fall back to a specific port
        ```
    """
    LOG.info("Auto-detecting serial communication port.")
    # Get the available ports.
    ports = serial.tools.list_ports.comports(include_links=False)
    candidates = []
    for port in ports:
        LOG.debug("Found port: %s", port.description)
        if _is_mscript_device(port):
            candidates.append(port)

    if len(candidates) != 1:
        LOG.error("%d candidates found. Auto detect failed.", len(candidates))
        raise Exception("Auto detection of serial port failed.")

    LOG.info("Exactly one candidate found. Using %s.", port.device)
    return candidates[0].device


class Serial:
    """Serial communication interface for EmStat Pico and other PalmSens devices.

    This class provides a wrapper around the pyserial library for communicating
    with PalmSens devices via a serial port. It is designed to be used with the
    Instrument class from pico_instrument.py.

    The class can be used as a context manager with the 'with' statement to ensure
    proper opening and closing of the port.

    Attributes:
        connection: The underlying pyserial Serial object.

    Examples:
        ```python
        from hardpotato.pico_serial import Serial, auto_detect_port
        from hardpotato.pico_instrument import Instrument

        # Use auto-detection to find the port
        try:
            port = auto_detect_port()
        except Exception:
            port = 'COM3'  # Fall back to a specific port

        # Using as a context manager (recommended)
        with Serial(port, timeout=1) as comm:
            instrument = Instrument(comm)
            instrument.get_device_type()

        # Using without a context manager
        comm = Serial(port, timeout=1)
        comm.open()
        instrument = Instrument(comm)
        # ... do operations ...
        comm.close()
        ```
    """

    def __init__(self, port: str, timeout: float) -> None:
        """Initialize the serial communication interface.

        Args:
            port: The serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux).
            timeout: Read timeout in seconds. A value of None means wait indefinitely.

        Note:
            This initializes the interface but does not open the port.
            Call open() or use the context manager to open the port.
        """
        self.connection = serial.Serial(port=None, baudrate=230400, timeout=timeout)
        self.connection.port = port

    def __enter__(self) -> "Serial":
        """Enter the context manager and open the port if needed.

        Returns:
            The Serial instance.
        """
        if not self.connection.is_open:
            self.open()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Exit the context manager and close the port."""
        self.close()

    def open(self) -> None:
        """Open the serial port.

        Raises:
            SerialException: If the port cannot be opened.
        """
        self.connection.open()

    def close(self) -> None:
        """Close the serial port."""
        self.connection.close()

    def write(self, data: bytes) -> None:
        """Write binary data to the serial port.

        Args:
            data: The binary data to write.

        Raises:
            SerialException: If the write operation fails.
        """
        self.connection.write(data)

    def readline(self) -> bytes:
        """Read a line from the serial port.

        Returns:
            bytes: The data read from the port, including the line ending.

        Note:
            This method blocks until a newline character is received, the timeout
            occurs, or the specified number of bytes is read.
            An empty bytes object is returned on timeout.
        """
        return self.connection.readline()

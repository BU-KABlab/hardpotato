import os
from typing import Any, List


class Test:
    """Test class for the chi1205b module.

    This class is primarily used for testing and debugging purposes.
    """

    def __init__(self) -> None:
        """Initialize the Test class and print confirmation message."""
        print("Test from chi1205b translator")


def check_connection(path: str) -> bool:
    """Check if a connection can be made to the CHI1205B potentiostat.

    This function checks if the required CHI software exists at the specified path.

    Args:
        path: The path to the CHI software installation.

    Returns:
        bool: True if the connection check is successful, False otherwise.
    """
    try:
        # Check if the CHI software executable exists at the specified path
        chi_exe = os.path.join(path, "chi1205b.exe")
        if os.path.exists(chi_exe):
            print("CHI1205B software found at", path)
            return True
        else:
            print("CHI1205B software not found at", path)
            print("Expected executable:", chi_exe)
            return False
    except Exception as e:
        print(f"Error checking CHI1205B connection: {str(e)}")
        return False


class Info:
    """Information class for CH Instruments 1205B potentiostat capabilities.

    This class stores the specifications and limitations of the CH Instruments 1205B
    potentiostat, including available techniques, options, and parameter limits.

    Attributes:
        tech: List of supported electrochemical techniques.
        options: List of additional parameters that can be specified.
        E_min: Minimum potential value in V.
        E_max: Maximum potential value in V.
        sr_min: Minimum scan rate in V/s.
        sr_max: Maximum scan rate in V/s.

    Pending:
    * Calculate dE, sr, dt, ttot, mins and max
    """

    def __init__(self) -> None:
        """Initialize the Info class with default specifications."""
        self.tech: List[str] = ["CV", "CA", "LSV", "OCP"]
        self.options: List[str] = ["Quiet time in s (qt)"]

        self.E_min: float = -2.4
        self.E_max: float = 2.4
        self.sr_min: float = 0.000001
        self.sr_max: float = 10
        # self.dE_min =
        # self.sr_min =
        # self.dt_min =
        # self.dt_max =
        # self.ttot_min =
        # self.ttot_max =

    def limits(
        self, val: float, low: float, high: float, label: str, units: str
    ) -> None:
        """Validate that a parameter value is within allowed limits.

        Args:
            val: The value to check.
            low: The minimum allowed value.
            high: The maximum allowed value.
            label: The name of the parameter for error messages.
            units: The units of the parameter for error messages.

        Raises:
            Exception: If the value is outside the allowed limits.
        """
        if val < low or val > high:
            raise ValueError(
                label
                + " should be between "
                + str(low)
                + " "
                + units
                + " and "
                + str(high)
                + " "
                + units
                + ". Received "
                + str(val)
                + " "
                + units
            )

    def specifications(self) -> None:
        """Print the specifications of the CH Instruments 1205B potentiostat."""
        print("Model: CH Instruments 1205B (chi1205b)")
        print("Techiques available:", self.tech)
        print("Options available:", self.options)


class CV:
    """Cyclic Voltammetry (CV) implementation for CH Instruments 1205B potentiostat.

    This class handles the generation of the macro commands to run
    Cyclic Voltammetry experiments on the CHI1205B potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body with file saving commands.
        foot: Footer section of the macro.

    Args:
        Eini: Initial potential in V.
        Ev1: First vertex potential in V.
        Ev2: Second vertex potential in V.
        Efin: Final potential in V.
        sr: Scan rate in V/s.
        dE: Potential increment in V.
        nSweeps: Number of sweeps.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters:
            qt: Quiet time in seconds before the experiment (default: 2).
    """

    def __init__(
        self,
        Eini: float,
        Ev1: float,
        Ev2: float,
        Efin: float,
        sr: float,
        dE: float,
        nSweeps: int,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the CV class and generate the macro commands.

        Args:
            Eini: Initial potential in V.
            Ev1: First vertex potential in V.
            Ev2: Second vertex potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            nSweeps: Number of sweeps.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2

        self.validate(Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens)

        # correcting parameters:
        Ei = Eini
        if Ev1 > Ev2:
            eh = Ev1
            el = Ev2
            pn = "p"
        else:
            eh = Ev2
            el = Ev1
            pn = "n"
        # nSweeps = nSweeps + 1 # final e from chi is enabled by default

        # building macro:
        self.head = (
            "c\x02\0\0\nfolder: "
            + folder
            + "\nfileoverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=cv\nei="
            + str(Ei)
            + "\neh="
            + str(eh)
            + "\nel="
            + str(el)
            + "\npn="
            + pn
            + "\ncl="
            + str(nSweeps)
            + "\nefon\nef="
            + str(Efin)
            + "\nsi="
            + str(dE)
            + "\nqt="
            + str(qt)
            + "\nv="
            + str(sr)
            + "\nsens="
            + str(sens)
        )
        self.body2 = (
            self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
        )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

    def validate(
        self,
        Eini: float,
        Ev1: float,
        Ev2: float,
        Efin: float,
        sr: float,
        dE: float,
        nSweeps: int,
        sens: float,
    ) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            Eini: Initial potential in V.
            Ev1: First vertex potential in V.
            Ev2: Second vertex potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            nSweeps: Number of sweeps.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside its allowed range.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Ev1, info.E_min, info.E_max, "Ev1", "V")
        info.limits(Ev2, info.E_min, info.E_max, "Ev2", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        info.limits(sr, info.sr_min, info.sr_max, "sr", "V/s")
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print("All the parameters are valid")


class LSV:
    """Linear Sweep Voltammetry (LSV) implementation for CH Instruments 1205B potentiostat.

    This class handles the generation of the macro commands to run
    Linear Sweep Voltammetry experiments on the CHI1205B potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body with file saving commands.
        foot: Footer section of the macro.

    Args:
        Eini: Initial potential in V.
        Efin: Final potential in V.
        sr: Scan rate in V/s.
        dE: Potential increment in V.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters:
            qt: Quiet time in seconds before the experiment (default: 2).
    """

    def __init__(
        self,
        Eini: float,
        Efin: float,
        sr: float,
        dE: float,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the LSV class and generate the macro commands.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2

        self.validate(Eini, Efin, sr, dE, sens)

        self.head = (
            "C\x02\0\0\nfolder: "
            + folder
            + "\nfileoverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=lsv\nei="
            + str(Eini)
            + "\nef="
            + str(Efin)
            + "\nv="
            + str(sr)
            + "\nsi="
            + str(dE)
            + "\nqt="
            + str(qt)
            + "\nsens="
            + str(sens)
        )
        self.body2 = (
            self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
        )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

    def validate(
        self, Eini: float, Efin: float, sr: float, dE: float, sens: float
    ) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside its allowed range.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        info.limits(sr, info.sr_min, info.sr_max, "sr", "V/s")
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print("All the parameters are valid")


class CA:
    """Chronoamperometry (CA) implementation for CH Instruments 1205B potentiostat.

    This class handles the generation of the macro commands to run
    Chronoamperometry experiments on the CHI1205B potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body with file saving commands.
        foot: Footer section of the macro.

    Args:
        Estep: Potential step in V.
        dt: Time interval in s.
        ttot: Total experiment time in s.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters:
            qt: Quiet time in seconds before the experiment (default: 2).
    """

    def __init__(
        self,
        Estep: float,
        dt: float,
        ttot: float,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the CA class and generate the macro commands.

        Args:
            Estep: Potential step in V.
            dt: Time interval in s.
            ttot: Total experiment time in s.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2

        self.head = (
            "C\x02\0\0\nfolder: "
            + folder
            + "\nfileoverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=i-t\nei="
            + str(Estep)
            + "\nst="
            + str(ttot)
            + "\nsi="
            + str(dt)
            + "\nqt="
            + str(qt)
            + "\nsens="
            + str(sens)
        )
        self.body2 = (
            self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
        )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

        self.validate(Estep, dt, ttot, sens)

    def validate(self, Estep: float, dt: float, ttot: float, sens: float) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            Estep: Potential step in V.
            dt: Time interval in s.
            ttot: Total experiment time in s.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside its allowed range.
        """
        info = Info()
        info.limits(Estep, info.E_min, info.E_max, "Estep", "V")
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print("All the parameters are valid")


class OCP:
    """Open Circuit Potential (OCP) implementation for CH Instruments 1205B potentiostat.

    This class handles the generation of the macro commands to run
    Open Circuit Potential experiments on the CHI1205B potentiostat.

    Attributes:
        ttot: Total experiment time in s.
        dt: Time interval in s.
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        foot: Footer section of the macro.

    Notes:
        Assumes OCP is between +- 5 V.

    Args:
        ttot: Total experiment time in s.
        dt: Time interval in s.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters:
            qt: Quiet time in seconds before the experiment (default: 2).
    """

    def __init__(
        self,
        ttot: float,
        dt: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the OCP class and generate the macro commands.

        Args:
            ttot: Total experiment time in s.
            dt: Time interval in s.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
        """
        self.ttot = ttot
        self.dt = dt

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2

        self.validate(ttot, dt)

        self.fileName = fileName
        self.folder = folder
        self.text = ""
        self.head = (
            "C\x02\0\0\nfolder: "
            + folder
            + "\nfileoverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=ocpt\nst="
            + str(ttot)
            + "\neh=5"
            + "\nel=-5"
            + "\nsi="
            + str(dt)
            + "\nqt="
            + str(qt)
            + "\nrun\nsave:"
            + self.fileName
            + "\ntsave:"
            + self.fileName
        )
        self.foot = "\nforcequit: yesiamsure\n"
        self.text = self.head + self.body + self.foot

    def validate(self, ttot: float, dt: float) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            ttot: Total experiment time in s.
            dt: Time interval in s.

        Raises:
            Exception: If any parameter is outside its allowed range.
        """
        _ = Info()
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        print("All the parameters are valid")


class DPV:
    """Differential Pulse Voltammetry (DPV) implementation for CH Instruments 1205B potentiostat.

    This class handles the generation of the macro commands to run
    Differential Pulse Voltammetry experiments on the CHI1205B potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body with file saving commands.
        foot: Footer section of the macro.

    Args:
        Eini: Initial potential in V.
        Efin: Final potential in V.
        Epulse: Pulse amplitude in V.
        Estep: Step potential in V.
        tpulse: Pulse width in s.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters:
            qt: Quiet time in seconds before the experiment (default: 2).
    """

    def __init__(
        self,
        Eini: float,
        Efin: float,
        Epulse: float,
        Estep: float,
        tpulse: float,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the DPV class and generate the macro commands.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            Epulse: Pulse amplitude in V.
            Estep: Step potential in V.
            tpulse: Pulse width in s.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2

        self.validate(Eini, Efin, Epulse, Estep, tpulse, sens)

        self.head = (
            "C\x02\0\0\nfolder: "
            + folder
            + "\nfileoverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=dpv\nei="
            + str(Eini)
            + "\nef="
            + str(Efin)
            + "\nph="
            + str(Epulse)
            + "\nsi="
            + str(Estep)
            + "\npw="
            + str(tpulse)
            + "\nqt="
            + str(qt)
            + "\nsens="
            + str(sens)
        )
        self.body2 = (
            self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
        )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

    def validate(
        self,
        Eini: float,
        Efin: float,
        Epulse: float,
        Estep: float,
        tpulse: float,
        sens: float,
    ) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            Epulse: Pulse amplitude in V.
            Estep: Step potential in V.
            tpulse: Pulse width in s.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside its allowed range.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        # info.limits(Epulse, info.Epulse_min, info.Epulse_max, 'Epulse', 'V')
        # info.limits(Estep, info.Estep_min, info.Estep_max, 'Estep', 'V')
        # info.limits(tpulse, info.tpulse_min, info.tpulse_max, 'tpulse', 's')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print("All the parameters are valid")


class SWV:
    """Square Wave Voltammetry (SWV) implementation for CH Instruments 1205B potentiostat.

    This class handles the generation of the macro commands to run
    Square Wave Voltammetry experiments on the CHI1205B potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body with file saving commands.
        foot: Footer section of the macro.

    Args:
        Eini: Initial potential in V.
        Efin: Final potential in V.
        Epulse: Pulse amplitude in V.
        Estep: Step potential in V.
        freq: Frequency in Hz.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters:
            qt: Quiet time in seconds before the experiment (default: 2).
    """

    def __init__(
        self,
        Eini: float,
        Efin: float,
        Epulse: float,
        Estep: float,
        freq: float,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the SWV class and generate the macro commands.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            Epulse: Pulse amplitude in V.
            Estep: Step potential in V.
            freq: Frequency in Hz.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2

        self.validate(Eini, Efin, Epulse, Estep, freq, sens)
        self.head = (
            "C\x02\0\0\nfolder: "
            + folder
            + "\nfileoverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=swv\nei="
            + str(Eini)
            + "\nef="
            + str(Efin)
            + "\nesw="
            + str(Epulse)
            + "\nsi="
            + str(Estep)
            + "\nfreq="
            + str(freq)
            + "\nqt="
            + str(qt)
            + "\nsens="
            + str(sens)
        )
        self.body2 = (
            self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
        )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

    def validate(
        self,
        Eini: float,
        Efin: float,
        Epulse: float,
        Estep: float,
        freq: float,
        sens: float,
    ) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            Epulse: Pulse amplitude in V.
            Estep: Step potential in V.
            freq: Frequency in Hz.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside its allowed range.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        # info.limits(Epulse, info.Epulse_min, info.Epulse_max, 'Epulse', 'V')
        # info.limits(Estep, info.Estep_min, info.Estep_max, 'Estep', 'V')
        # info.limits(freq, info.freq_min, info.freq_max, 'freq', 'Hz')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print("All the parameters are valid")

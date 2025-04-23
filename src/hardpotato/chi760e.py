import os
from typing import Any, List


class Test:
    """Test class for the chi760e module.

    This class is primarily used for testing and debugging purposes.
    """

    def __init__(self) -> None:
        """Initialize the Test class and print confirmation message."""
        print("Test from chi760e translator")


def check_connection(path: str) -> bool:
    """Check if a connection can be made to the CHI760E potentiostat.

    This function checks if the required CHI software exists at the specified path.

    Args:
        path: The path to the CHI software installation.

    Returns:
        bool: True if the connection check is successful, False otherwise.
    """
    try:
        # Check if the CHI software executable exists at the specified path
        chi_exe = os.path.join(path, "chi760e.exe")
        if os.path.exists(chi_exe):
            print("CHI760E software found at", path)
            return True
        else:
            print("CHI760E software not found at", path)
            print("Expected executable:", chi_exe)
            return False
    except Exception as e:
        print(f"Error checking CHI760E connection: {str(e)}")
        return False


class Info:
    """Information class for CH Instruments 760E potentiostat capabilities.

    This class stores the specifications and limitations of the CH Instruments 760E
    potentiostat, including available techniques, options, and parameter limits.
    The 760E features bipotentiostat capabilities for dual working electrode experiments.

    Attributes:
        tech: List of supported electrochemical techniques.
        options: List of additional parameters that can be specified.
        E_min: Minimum potential value in V.
        E_max: Maximum potential value in V.
        sr_min: Minimum scan rate in V/s.
        sr_max: Maximum scan rate in V/s.
        freq_min: Minimum frequency for EIS in Hz.
        freq_max: Maximum frequency for EIS in Hz.

    Pending:
    * Calculate dE, sr, dt, ttot, mins and max
    """

    def __init__(self) -> None:
        """Initialize the Info class with default specifications for CHI760E."""
        self.tech: List[str] = ["CV", "CA", "LSV", "OCP", "NPV", "EIS"]
        self.options: List[str] = [
            "Quiet time in s (qt)",
            "Resistance in ohms (resistance)",
        ]

        self.E_min: float = -10
        self.E_max: float = 10
        self.sr_min: float = 0.000001
        self.sr_max: float = 10000
        # self.dE_min =
        # self.sr_min =
        # self.dt_min =
        # self.dt_max =
        # self.ttot_min =
        # self.ttot_max =
        self.freq_min: float = 0.00001
        self.freq_max: float = 1000000

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
        """Print the specifications of the CH Instruments 760E potentiostat."""
        print("Model: CH Instruments 760E (chi760e)")
        print("Techiques available:", self.tech)
        print("Options available:", self.options)


class CV:
    """Cyclic Voltammetry (CV) implementation for CH Instruments 760E potentiostat.

    This class handles the generation of the macro commands to run
    Cyclic Voltammetry experiments on the CHI760E potentiostat, which
    includes bipotentiostat capabilities.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body including IR compensation or bipotentiostat commands.
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
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).
        resistance: Solution resistance in ohms for IR compensation (default: 0).
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
        """Initialize a Cyclic Voltammetry experiment for CHI760E.

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
                resistance: Solution resistance in ohms for IR compensation (default: 0).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2
        if "resistance" in kwargs:
            resistance = kwargs.get("resistance")
        else:
            resistance = 0

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
        nSweeps = nSweeps + 1  # final e from chi is enabled by default

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
        if resistance:  # In case IR compensation is required
            self.body2 = (
                self.body
                + "\nmir="
                + str(resistance)
                + "\nircompon\nrun\nircompoff\nsave:"
                + self.fileName
                + "\ntsave:"
                + self.fileName
            )
        else:
            self.body2 = (
                self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
            )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

    def bipot(self, E: float, sens: float) -> None:
        """Configure the experiment for bipotentiostat mode.

        This enables the second working electrode at a fixed potential
        for dual working electrode experiments, which is a feature specific
        to the CHI760E model.

        Args:
            E: Potential for second working electrode in V.
            sens: Sensitivity for second working electrode in A/V.
        """
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E2", "V")
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

        self.body2 = (
            self.body
            + "\ne2="
            + str(E)
            + "\nsens2="
            + str(sens)
            + "\ni2on"
            + "\nrun\nsave:"
            + self.fileName
            + "\ntsave:"
            + self.fileName
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
            Exception: If any parameter is outside the allowed limits.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Ev1, info.E_min, info.E_max, "Ev1", "V")
        info.limits(Ev2, info.E_min, info.E_max, "Ev2", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        info.limits(sr, info.sr_min, info.sr_max, "sr", "V/s")
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')


class LSV:
    """Linear Sweep Voltammetry (LSV) implementation for CH Instruments 760E potentiostat.

    This class handles the generation of the macro commands to run
    Linear Sweep Voltammetry experiments on the CHI760E potentiostat, which
    includes bipotentiostat capabilities.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body including IR compensation or bipotentiostat commands.
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
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).
        resistance: Solution resistance in ohms for IR compensation (default: 0).
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
        """Initialize a Linear Sweep Voltammetry experiment for CHI760E.

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
                resistance: Solution resistance in ohms for IR compensation (default: 0).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2
        if "resistance" in kwargs:
            resistance = kwargs.get("resistance")
        else:
            resistance = 0

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
        if resistance:  # In case IR compensation is required
            self.body2 = (
                self.body
                + "\nmir="
                + str(resistance)
                + "\nircompon\nrun\nircompoff\nsave:"
                + self.fileName
                + "\ntsave:"
                + self.fileName
            )
        else:
            self.body2 = (
                self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
            )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

    def bipot(self, E: float, sens: float) -> None:
        """Configure the experiment for bipotentiostat mode.

        This enables the second working electrode at a fixed potential
        for dual working electrode experiments, which is a feature specific
        to the CHI760E model.

        Args:
            E: Potential for second working electrode in V.
            sens: Sensitivity for second working electrode in A/V.
        """
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E2", "V")
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

        self.body2 = (
            self.body
            + "\ne2="
            + str(E)
            + "\nsens2="
            + str(sens)
            + "\ni2on"
            + "\nrun\nsave:"
            + self.fileName
            + "\ntsave:"
            + self.fileName
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
            Exception: If any parameter is outside the allowed limits.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        info.limits(sr, info.sr_min, info.sr_max, "sr", "V/s")
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')


class NPV:
    """Normal Pulse Voltammetry (NPV) implementation for CH Instruments 760E potentiostat.

    This class handles the generation of the macro commands to run
    Normal Pulse Voltammetry experiments on the CHI760E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        foot: Footer section of the macro.

    Args:
        Eini: Initial potential in V.
        Efin: Final potential in V.
        dE: Potential increment in V.
        tsample: Sample width in s.
        twidth: Pulse width in s.
        tperiod: Pulse period in s.
        sens: Sensitivity in A/V.
        path_lib: Path to the CHI library.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).

    Note:
        This technique is still in development. Use with caution.
    """

    def __init__(
        self,
        Eini: float,
        Efin: float,
        dE: float,
        tsample: float,
        twidth: float,
        tperiod: float,
        sens: float,
        path_lib: str,
        folder: str,
        fileName: str,
        header: str,
        **kwargs: Any,
    ) -> None:
        """Initialize a Normal Pulse Voltammetry experiment for CHI760E.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            dE: Potential increment in V.
            tsample: Sample width in s.
            twidth: Pulse width in s.
            tperiod: Pulse period in s.
            sens: Sensitivity in A/V.
            path_lib: Path to the CHI library.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
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

        print("NPV technique still in development. Use with caution.")

        self.validate(Eini, Efin, dE, tsample, twidth, tperiod, sens)

        self.head = (
            "C\x02\0\0\nfolder: "
            + folder
            + "\nfileOverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=NPV\nei="
            + str(Eini)
            + "\nef="
            + str(Efin)
            + "\nincre="
            + str(dE)
            + "\npw="
            + str(tsample)
            + "\nsw="
            + str(twidth)
            + "\nprod="
            + str(tperiod)
            + "\nqt="
            + str(qt)
            + "\nsens="
            + str(sens)
        )
        self.body = self.body + "\nrun\nsave:" + fileName + "\ntsave:" + fileName
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body + self.foot

    def validate(
        self,
        Eini: float,
        Efin: float,
        dE: float,
        tsample: float,
        twidth: float,
        tperiod: float,
        sens: float,
    ) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            dE: Potential increment in V.
            tsample: Sample width in s.
            twidth: Pulse width in s.
            tperiod: Pulse period in s.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside the allowed limits.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        # info.limits(tsample, info.tsample)
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')


class CA:
    """Chronoamperometry (CA) implementation for CH Instruments 760E potentiostat.

    This class handles the generation of the macro commands to run
    Chronoamperometry experiments on the CHI760E potentiostat, which
    includes bipotentiostat capabilities.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body including IR compensation or bipotentiostat commands.
        foot: Footer section of the macro.

    Args:
        Estep: Step potential in V.
        dt: Time increment for data collection in s.
        ttot: Total time of the experiment in s.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).
        resistance: Solution resistance in ohms for IR compensation (default: 0).
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
        """Initialize a Chronoamperometry experiment for CHI760E.

        Args:
            Estep: Step potential in V.
            dt: Time increment for data collection in s.
            ttot: Total time of the experiment in s.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
                resistance: Solution resistance in ohms for IR compensation (default: 0).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2
        if "resistance" in kwargs:
            resistance = kwargs.get("resistance")
        else:
            resistance = 0

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
        if resistance:  # In case IR compensation is required
            self.body2 = (
                self.body
                + "\nmir="
                + str(resistance)
                + "\nircompon\nrun\nircompoff\nsave:"
                + self.fileName
                + "\ntsave:"
                + self.fileName
            )
        else:
            self.body2 = (
                self.body + "\nrun\nsave:" + self.fileName + "\ntsave:" + self.fileName
            )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot

        self.validate(Estep, dt, ttot, sens)

    def validate(self, Estep: float, dt: float, ttot: float, sens: float) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            Estep: Step potential in V.
            dt: Time increment for data collection in s.
            ttot: Total time of the experiment in s.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside the allowed limits.
        """
        info = Info()
        info.limits(Estep, info.E_min, info.E_max, "Estep", "V")
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

    def bipot(self, E: float, sens: float) -> None:
        """Configure the experiment for bipotentiostat mode.

        This enables the second working electrode at a fixed potential
        for dual working electrode experiments, which is a feature specific
        to the CHI760E model.

        Args:
            E: Potential for second working electrode in V.
            sens: Sensitivity for second working electrode in A/V.
        """
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E2", "V")
        # info.limits(sens, info.sens_min, info.sens_max, 'sens2', 'A/V')
        self.body2 = (
            self.body
            + "\ne2="
            + str(E)
            + "\nsens2="
            + str(sens)
            + "\ni2on"
            + "\nrun\nsave:"
            + self.fileName
            + "\ntsave:"
            + self.fileName
        )
        self.foot = "\n forcequit: yesiamsure\n"
        self.text = self.head + self.body2 + self.foot


class OCP:
    """Open Circuit Potential (OCP) measurement implementation for CH Instruments 760E potentiostat.

    This class handles the generation of the macro commands to run
    Open Circuit Potential measurements on the CHI760E potentiostat.
    The measurement assumes the OCP will be between -10V and +10V.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        foot: Footer section of the macro.

    Args:
        ttot: Total measurement time in s.
        dt: Time increment for data collection in s.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).
        resistance: Solution resistance in ohms for IR compensation (default: 0).

    Note:
        Assumes OCP is between ±10 V.
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
        """Initialize an Open Circuit Potential measurement for CHI760E.

        Args:
            ttot: Total measurement time in s.
            dt: Time increment for data collection in s.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
                resistance: Solution resistance in ohms for IR compensation (default: 0).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2
        # if "resistance" in kwargs:
        #     resistance = kwargs.get("resistance")
        # else:
        #     resistance = 0

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
            + "\neh=10"
            + "\nel=-10"
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

        self.validate(ttot, dt)

    def validate(self, ttot: float, dt: float) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            ttot: Total measurement time in s.
            dt: Time increment for data collection in s.

        Raises:
            Exception: If any parameter is outside the allowed limits.
        """
        _ = Info()
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        pass


class EIS:
    """Electrochemical Impedance Spectroscopy (EIS) implementation for CH Instruments 760E potentiostat.

    This class handles the generation of the macro commands to run
    Electrochemical Impedance Spectroscopy experiments on the CHI760E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        foot: Footer section of the macro.

    Args:
        Eini: DC potential offset in V.
        low_freq: Lower frequency limit in Hz.
        high_freq: Upper frequency limit in Hz.
        amplitude: AC amplitude in V.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).

    Note:
        This technique is still in development. Use with caution.

    Pending:
    * Validate parameters
    """

    def __init__(
        self,
        Eini: float,
        low_freq: float,
        high_freq: float,
        amplitude: float,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize an Electrochemical Impedance Spectroscopy experiment for CHI760E.

        Args:
            Eini: DC potential offset in V.
            low_freq: Lower frequency limit in Hz.
            high_freq: Upper frequency limit in Hz.
            amplitude: AC amplitude in V.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
        """
        print("EIS technique is still in development. Use with caution.")
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
            "tech=imp\nei="
            + str(Eini)
            + "\nfl="
            + str(low_freq)
            + "\nfh="
            + str(high_freq)
            + "\namp="
            + str(amplitude)
            + "\nsens="
            + str(sens)
            + "\nqt="
            + str(qt)
            + "\nrun\nsave:"
            + self.fileName
            + "\ntsave:"
            + self.fileName
        )
        self.foot = "\nforcequit: yesiamsure\n"
        self.text = self.head + self.body + self.foot

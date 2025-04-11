from typing import Any, List


class Test:
    """Test class for the chi601e module.

    This class is primarily used for testing and debugging purposes.
    """

    def __init__(self) -> None:
        """Initialize the Test class and print confirmation message."""
        print("Test from chi601e translator")


class Info:
    """Information class for CH Instruments 601E potentiostat capabilities.

    This class stores the specifications and limitations of the CH Instruments 601E
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
        # self.freq_min = 0.00001
        # self.freq_max = 1000000

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
            raise Exception(
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
        """Print the specifications of the CH Instruments 601E potentiostat."""
        print("Model: CH Instruments 601E (chi601e)")
        print("Techiques available:", self.tech)
        print("Options available:", self.options)


class CV:
    """Cyclic Voltammetry (CV) implementation for CH Instruments 601E potentiostat.

    This class handles the generation of the macro commands to run
    Cyclic Voltammetry experiments on the CHI601E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body including IR compensation if needed.
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
            resistance: Solution resistance in ohms for IR compensation (default: 0).

    **kwargs:
        qt: Quiet time in seconds before the experiment.
        resistance: Solution resistance in ohms for IR compensation.
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
        """Initialize a Cyclic Voltammetry experiment for CHI601E.

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
    """Linear Sweep Voltammetry (LSV) implementation for CH Instruments 601E potentiostat.

    This class handles the generation of the macro commands to run
    Linear Sweep Voltammetry experiments on the CHI601E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body including IR compensation if needed.
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
        """Initialize a Linear Sweep Voltammetry experiment for CHI601E.

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
    """Normal Pulse Voltammetry (NPV) implementation for CH Instruments 601E potentiostat.

    This class handles the generation of the macro commands to run
    Normal Pulse Voltammetry experiments on the CHI601E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        foot: Footer section of the macro.

    Note:
        This technique is still in development and should be used with caution.

    Args:
        Eini: Initial potential in V.
        Efin: Final potential in V.
        dE: Potential increment in V.
        tsample: Sampling time in s.
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
        """Initialize a Normal Pulse Voltammetry experiment for CHI601E.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            dE: Potential increment in V.
            tsample: Sampling time in s.
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
            + "\n"
            + fileOverride
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
            tsample: Sampling time in s.
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
    """Chronoamperometry (CA) implementation for CH Instruments 601E potentiostat.

    This class handles the generation of the macro commands to run
    Chronoamperometry (i-t curve) experiments on the CHI601E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        body2: Extended body including IR compensation if needed.
        foot: Footer section of the macro.

    Args:
        Estep: Step potential in V.
        dt: Time interval in s.
        ttot: Total experiment time in s.
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
        """Initialize a Chronoamperometry experiment for CHI601E.

        Args:
            Estep: Step potential in V.
            dt: Time interval in s.
            ttot: Total experiment time in s.
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
            dt: Time interval in s.
            ttot: Total experiment time in s.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside the allowed limits.
        """
        info = Info()
        info.limits(Estep, info.E_min, info.E_max, "Estep", "V")
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')


class OCP:
    """Open Circuit Potential (OCP) implementation for CH Instruments 601E potentiostat.

    This class handles the generation of the macro commands to run
    Open Circuit Potential measurements on the CHI601E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        foot: Footer section of the macro.

    Note:
        This implementation assumes the OCP is between ±10 V.

    Args:
        ttot: Total experiment time in s.
        dt: Time interval in s.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).
        resistance: Solution resistance in ohms (default: 0).
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
        """Initialize an Open Circuit Potential measurement for CHI601E.

        Args:
            ttot: Total experiment time in s.
            dt: Time interval in s.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
                resistance: Solution resistance in ohms (default: 0).
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
            ttot: Total experiment time in s.
            dt: Time interval in s.

        Raises:
            Exception: If any parameter is outside the allowed limits.
        """
        info = Info()
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')


class EIS:
    """Electrochemical Impedance Spectroscopy (EIS) implementation for CH Instruments 601E potentiostat.

    This class handles the generation of the macro commands to run
    Electrochemical Impedance Spectroscopy measurements on the CHI601E potentiostat.

    Attributes:
        fileName: Base name for the output files.
        folder: Path to the folder where files will be saved.
        text: The macro commands to send to the potentiostat.
        head: Header section of the macro.
        body: Main section of the macro with experiment parameters.
        foot: Footer section of the macro.

    Args:
        E: DC potential in V.
        freqini: Initial frequency in Hz.
        freqfin: Final frequency in Hz.
        amp: AC amplitude in V.
        nfreq: Number of frequency points.
        sens: Sensitivity in A/V.
        folder: Directory to save results.
        fileName: Base name for output files.
        header: Header text for the output files.
        path_lib: Path to the CHI library.
        **kwargs: Additional optional parameters.

    **kwargs:
        qt: Quiet time in seconds before the experiment (default: 2).
        optSweep: Optimization sweep type for EIS (default: 1).
    """

    def __init__(
        self,
        E: float,
        freqini: float,
        freqfin: float,
        amp: float,
        nfreq: int,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: str,
        **kwargs: Any,
    ) -> None:
        """Initialize an Electrochemical Impedance Spectroscopy measurement for CHI601E.

        Args:
            E: DC potential in V.
            freqini: Initial frequency in Hz.
            freqfin: Final frequency in Hz.
            amp: AC amplitude in V.
            nfreq: Number of frequency points.
            sens: Sensitivity in A/V.
            folder: Directory to save results.
            fileName: Base name for output files.
            header: Header text for the output files.
            path_lib: Path to the CHI library.
            **kwargs: Additional optional parameters:
                qt: Quiet time in seconds before the experiment (default: 2).
                optSweep: Optimization sweep type for EIS (default: 1).
        """
        self.fileName = fileName
        self.folder = folder
        self.text = ""

        if "qt" in kwargs:
            qt = kwargs.get("qt")
        else:
            qt = 2

        if "optSweep" in kwargs:
            optSweep = kwargs.get("optSweep")
        else:
            optSweep = 1

        print("EIS: Selected AC amplitude:", amp, " V")

        # Verification steps:
        self.validate(E, freqini, freqfin, amp, sens)

        self.head = (
            "c\x02\0\0\nfolder: "
            + folder
            + "\nfileoverride\n"
            + "header: "
            + header
            + "\n\n"
        )
        self.body = (
            "tech=im\nip="
            + str(optSweep)  # 1: logarithmic sweep
            + "\neh="
            + str(E)
            + "\namp="
            + str(amp)
            + "\nfi="
            + str(freqini)
            + "\nfh="
            + str(freqfin)
            + "\nnt="
            + str(nfreq)  # number of freq. points
            + "\nqt="
            + str(qt)
            + "\nsens="
            + str(sens)
            + "\nrun\nimplot\nimproc=1\nimpchrt\ndt=0\nimpproc\nsave:"
            + self.fileName
            + "\ntsave:"
            + self.fileName
        )
        self.foot = "\nforcequit: yesiamsure\n"
        self.text = self.head + self.body + self.foot

    def validate(
        self, E: float, freqini: float, freqfin: float, amp: float, sens: float
    ) -> None:
        """Validate that all parameters are within allowed limits.

        Args:
            E: DC potential in V.
            freqini: Initial frequency in Hz.
            freqfin: Final frequency in Hz.
            amp: AC amplitude in V.
            sens: Sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside the allowed limits.
        """
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E", "V")
        # info.limits(freqini, info.freq_min, info.freq_max, 'freqini', 'Hz')
        # info.limits(freqfin, info.freq_min, info.freq_max, 'freqfin', 'Hz')
        # info.limits(amp, info.amp_min, info.amp_max, 'amp', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

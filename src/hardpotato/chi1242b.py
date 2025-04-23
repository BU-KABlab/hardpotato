"""
CH Instruments 1242B Potentiostat Interface Module

This module provides classes for controlling and running experiments on a CH Instruments 1242B
potentiostat. It includes support for Cyclic Voltammetry (CV), Chronoamperometry (CA),
Linear Sweep Voltammetry (LSV), and Open Circuit Potential (OCP) measurements.

Classes:
    Test: Simple test class for verifying module import
    Info: Contains specifications and validation methods for the instrument
    CV: Sets up and validates cyclic voltammetry experiments
    LSV: Sets up and validates linear sweep voltammetry experiments
    CA: Sets up and validates chronoamperometry experiments
    OCP: Sets up and validates open circuit potential measurements
"""

import os


class Test:
    """A simple test class to verify the module is imported correctly."""

    def __init__(self):
        print("Test from chi1242b translator")


def check_connection(path: str) -> bool:
    """Check if a connection can be made to the CHI1242B potentiostat.
    
    This function checks if the required CHI software exists at the specified path.
    
    Args:
        path: The path to the CHI software installation.
        
    Returns:
        bool: True if the connection check is successful, False otherwise.
    """
    try:
        # Check if the CHI software executable exists at the specified path
        chi_exe = os.path.join(path, "chi1242b.exe")
        if os.path.exists(chi_exe):
            print("CHI1242B software found at", path)
            return True
        else:
            print("CHI1242B software not found at", path)
            print("Expected executable:", chi_exe)
            return False
    except Exception as e:
        print(f"Error checking CHI1242B connection: {str(e)}")
        return False


class Info:
    """
    Contains instrument specifications and validation methods.

    This class provides information about the CH Instruments 1242B potentiostat,
    including supported techniques, valid parameter ranges, and validation methods
    to ensure experiment parameters are within acceptable limits.

    Attributes:
        tech (list): List of supported techniques (CV, CA, LSV, OCP)
        options (list): List of available options
        E_min (float): Minimum voltage limit in volts
        E_max (float): Maximum voltage limit in volts
        sr_min (float): Minimum scan rate in V/s
        sr_max (float): Maximum scan rate in V/s
    """

    def __init__(self):
        self.tech = ["CV", "CA", "LSV", "OCP"]
        self.options = ["Quiet time in s (qt)"]

        self.E_min = -2.4
        self.E_max = 2.4
        self.sr_min = 0.000001
        self.sr_max = 10
        # self.dE_min =
        # self.sr_min =
        # self.dt_min =
        # self.dt_max =
        # self.ttot_min =
        # self.ttot_max =

    def limits(self, val, low, high, label, units):
        """
        Validates that a parameter value is within specified limits.

        Args:
            val: The parameter value to check
            low: The minimum allowed value
            high: The maximum allowed value
            label (str): The parameter name for error messages
            units (str): The units of the parameter for error messages

        Raises:
            Exception: If the parameter value is outside the specified limits
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

    def specifications(self):
        """
        Prints the specifications of the instrument including model name,
        available techniques, and options.
        """
        print("Model: CH Instruments 1242B (chi1242b)")
        print("Techiques available:", self.tech)
        print("Options available:", self.options)


class CV:
    """
    Sets up and validates cyclic voltammetry experiments.

    This class generates the necessary commands for running cyclic voltammetry
    experiments on a CH Instruments 1242B potentiostat. It validates parameters
    and constructs the appropriate command text.

    Args:
        Eini (float): Initial potential in volts
        Ev1 (float): First vertex potential in volts
        Ev2 (float): Second vertex potential in volts
        Efin (float): Final potential in volts
        sr (float): Scan rate in V/s
        dE (float): Potential step in V
        nSweeps (int): Number of sweep segments
        sens (float): Current sensitivity in A/V
        folder (str): Folder path for data storage
        fileName (str): Name of the output file
        header (str): Header information for the output file
        path_lib (str): Path to the library

    Keyword Args:
        qt (float, optional): Quiet time in seconds before experiment starts. Defaults to 2.
    """

    def __init__(
        self,
        Eini,
        Ev1,
        Ev2,
        Efin,
        sr,
        dE,
        nSweeps,
        sens,
        folder,
        fileName,
        header,
        path_lib,
        **kwargs,
    ):
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

    def bipot(self, E, sens):
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E2", "V")
        # info.limits(sens, info.senC:\Users\oliverrz\Desktop\CHI\chi760es_min, info.sens_max, 'sens', 'A/V')

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

    def validate(self, Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens):
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Ev1, info.E_min, info.E_max, "Ev1", "V")
        info.limits(Ev2, info.E_min, info.E_max, "Ev2", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        info.limits(sr, info.sr_min, info.sr_max, "sr", "V/s")
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')


class LSV:
    """
    Sets up and validates linear sweep voltammetry experiments.

    This class generates the necessary commands for running linear sweep voltammetry (LSV)
    measurements on a CH Instruments 1242B potentiostat. It validates parameters
    and constructs the appropriate command text.

    Args:
        Ei (float): Initial potential in volts
        Ef (float): Final potential in volts
        v (float): Scan rate in V/s
        folder (str): Folder path for data storage
        fileName (str): Name of the output file
        header (str): Header information for the output file
        path_lib (str): Path to the library

    Keyword Args:
        qt (float, optional): Quiet time in seconds before experiment starts. Defaults to 2.
        si (int, optional): Sensitivity in A/V. Defaults to 1e-6.
    """

    def __init__(
        self, Eini, Efin, sr, dE, sens, folder, fileName, header, path_lib, **kwargs
    ):
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

    def validate(self, Eini, Efin, sr, dE, sens):
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        info.limits(sr, info.sr_min, info.sr_max, "sr", "V/s")
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

    def bipot(self, E, sens):
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


class CA:
    """
    Sets up and validates chronoamperometry experiments.

    This class generates the necessary commands for running chronoamperometry (CA)
    measurements on a CH Instruments 1242B potentiostat. It validates parameters
    and constructs the appropriate command text.

    Args:
        Ei (float): Initial potential in volts
        Ef (float): Final potential in volts
        t1 (float): Time in seconds at initial potential
        t2 (float): Time in seconds at final potential
        si (float): Sensitivity in A/V
        folder (str): Folder path for data storage
        fileName (str): Name of the output file
        header (str): Header information for the output file
        path_lib (str): Path to the library

    Keyword Args:
        qt (float, optional): Quiet time in seconds before experiment starts. Defaults to 2.
    """

    def __init__(
        self, Estep, dt, ttot, sens, folder, fileName, header, path_lib, **kwargs
    ):
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

    def validate(self, Estep, dt, ttot, sens):
        info = Info()
        info.limits(Estep, info.E_min, info.E_max, "Estep", "V")
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

    def bipot(self, E, sens):
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
    """
    Sets up and validates open circuit potential experiments.

    This class generates the necessary commands for running open circuit potential (OCP)
    measurements on a CH Instruments 1242B potentiostat. It validates parameters
    and constructs the appropriate command text.

    Args:
        t (float): Duration time in seconds
        dt (float): Time interval for data sampling in seconds
        folder (str): Folder path for data storage
        fileName (str): Name of the output file
        header (str): Header information for the output file
        path_lib (str): Path to the library

    Keyword Args:
        qt (float, optional): Quiet time in seconds before experiment starts. Defaults to 2.
    """

    def __init__(self, ttot, dt, folder, fileName, header, path_lib, **kwargs):
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

    def validate(self, ttot, dt):
        _ = Info()
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')

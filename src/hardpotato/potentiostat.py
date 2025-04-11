import subprocess
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import softpotato as sp

import hardpotato.chi601e as chi601e
import hardpotato.chi760e as chi760e
import hardpotato.chi1205b as chi1205b
import hardpotato.chi1242b as chi1242b
import hardpotato.emstatpico as emstatpico
import hardpotato.load_data as load_data
import hardpotato.pico_instrument as instrument
import hardpotato.pico_mscript as mscript
import hardpotato.pico_serial as serial
import hardpotato.save_data as save_data

# Potentiostat models available:
models_available = ["chi1205b", "chi1242b", "chi601e", "chi760e", "emstatpico"]

# Global variables
folder_save = "."
model_pstat = "no pstat"
path_lib = "."


class Test:
    """Test class for the potentiostat module.

    This class is primarily used for testing and debugging purposes.
    """

    def __init__(self) -> None:
        """Initialize the Test class and print confirmation message."""
        print("Test from potentiostat module")


class Info:
    """Information class for potentiostats.

    Provides access to specifications and information about
    the selected potentiostat model.

    Attributes:
        model: The potentiostat model name.
        info: The specific info object for the selected potentiostat.
    """

    def __init__(self, model: str) -> None:
        """Initialize the Info class for a specific potentiostat model.

        Args:
            model: The potentiostat model name (e.g., "chi760e", "emstatpico").

        Note:
            If the specified model is not available, a message will be displayed
            with the available models.
        """
        self.model = model
        if self.model == "chi1205b":
            self.info = chi1205b.Info()
        elif self.model == "chi1242b":
            self.info = chi1242b.Info()
        elif self.model == "chi601e":
            self.info = chi601e.Info()
        elif self.model == "chi760e":
            self.info = chi760e.Info()
        elif self.model == "emstatpico":
            self.info = emstatpico.Info()
        else:
            print("Potentiostat model " + model + " not available in the library.")
            print("Available models:", models_available)

    def specifications(self) -> None:
        """Display the specifications of the potentiostat.

        This method prints out the specifications of the selected
        potentiostat model, such as available techniques and options.
        """
        self.info.specifications()


class Setup:
    """Setup class for configuring the potentiostat connection and parameters.

    This class initializes the global settings for the potentiostat, including
    the model, file paths, and save folders.

    Examples:
        ```python
        import hardpotato as hp

        # Basic setup with default values
        hp.potentiostat.Setup('emstatpico')

        # Full setup with custom paths
        hp.potentiostat.Setup(
            model='chi760e',
            path='C:/CHI/chi760e',
            folder='C:/Data',
            port='COM3',
            verbose=1
        )
        ```
    """

    def __init__(
        self,
        model: str = "0",
        path: str = ".",
        folder: str = ".",
        port: Optional[str] = None,
        verbose: int = 1,
    ) -> None:
        """Initialize the potentiostat setup.

        Args:
            model: The potentiostat model name (e.g., "chi760e", "emstatpico").
            path: The path to the potentiostat software or library. Not required for Emstat Pico.
            folder: The folder path where data will be saved.
            port: The serial port for the potentiostat connection (for devices like Emstat Pico).
            verbose: Whether to print setup information (1=True, 0=False).
        """
        global folder_save
        folder_save = folder
        global model_pstat
        model_pstat = model
        global path_lib
        path_lib = path
        global port_
        port_ = port
        if verbose:
            self.info()

    def info(self) -> None:
        """Display the current potentiostat setup.

        This method prints information about the current potentiostat configuration,
        including the model, path, and save folder location.
        """
        print("\n----------")
        print("Potentiostat model: " + model_pstat)
        print("Potentiostat path: " + path_lib)
        print("Save folder: " + folder_save)
        print("----------\n")


class Technique:
    """Base class for all electrochemical techniques.

    This class provides common functionality for all electrochemical techniques,
    including file I/O, running experiments, and plotting results.

    Attributes:
        text: The script text for the potentiostat.
        fileName: The base name for saving files.
        technique: The name of the technique.
        bpot: Flag indicating if bipotentiostat mode is active.

    Note:
        This class is not intended to be instantiated directly.
        Instead, use specific technique classes like CV, LSV, CA, etc.
    """

    def __init__(self, text: str = "", fileName: str = "CV") -> None:
        """Initialize the Technique base class.

        Args:
            text: The script text for the potentiostat.
            fileName: The base name for saving files.
        """
        self.text = text  # text to write as macro
        self.fileName = fileName
        self.technique = "Technique"
        self.bpot = False

    def writeToFile(self) -> None:
        """Write the technique script to a file.

        Creates a .mcr file for CHI potentiostats or a .mscr file for Emstat Pico,
        containing the script needed to run the experiment.
        """
        if model_pstat[0:3] == "chi":
            file = open(folder_save + "/" + self.fileName + ".mcr", "wb")
            file.write(self.text.encode("ascii"))
            file.close()
        elif model_pstat == "emstatpico":
            file = open(folder_save + "/" + self.fileName + ".mscr", "wb")
            file.write(self.text.encode("ascii"))
            file.close()

    def run(self) -> None:
        """Run the electrochemical technique.

        This method executes the experiment on the potentiostat, writes the data to files,
        and generates plots. The specific behavior depends on the potentiostat model:
        - For CHI potentiostats: writes a script file and calls the CHI software to execute it.
        - For Emstat Pico: communicates directly with the device via serial port.

        Raises:
            Various exceptions from subprocess.run or serial communication.
        """
        if model_pstat[0:3] == "chi":
            self.message()
            # Write macro:
            self.writeToFile()
            # Run command:
            print("Running CV")
            command = (
                f'"{path_lib}"'
                + ' /runmacro:"'
                + folder_save
                + "/"
                + self.fileName
                + '.mcr"'
            )
            subprocess.run(command)
            self.message(start=False)
            self.plot()
        elif model_pstat == "emstatpico":
            self.message()
            self.writeToFile()
            if port_ is None:
                self.port = serial.auto_detect_port()
            with serial.Serial(self.port, 1) as comm:
                dev = instrument.Instrument(comm)
                dev.send_script(folder_save + "/" + self.fileName + ".mscr")
                result = dev.readlines_until_end()
            self.data = mscript.parse_result_lines(result)
            fileName = folder_save + "/" + self.fileName + ".txt"
            save = save_data.Save(
                self.data,
                fileName,
                self.header,
                model_pstat,
                self.technique,
                bpot=self.bpot,
            )
            self.message(start=False)
            self.plot()
        else:
            print("\nNo potentiostat selected. Aborting.")

    def plot(self) -> None:
        """Plot the results of the electrochemical technique.

        This method generates and saves plots of the experimental data.
        The specific plot depends on the technique used (e.g., CV, LSV, CA, OCP).
        """
        figNum = np.random.randint(100)  # To prevent rewriting the same plot
        if self.technique == "CV":
            cv = load_data.CV(self.fileName + ".txt", folder_save, model_pstat)
            sp.plotting.plot(
                cv.E,
                cv.i,
                show=False,
                fig=figNum,
                fileName=folder_save + "/" + self.fileName,
            )
        elif self.technique == "LSV":
            lsv = load_data.LSV(self.fileName + ".txt", folder_save, model_pstat)
            sp.plotting.plot(
                lsv.E,
                lsv.i,
                show=False,
                fig=figNum,
                fileName=folder_save + "/" + self.fileName,
            )
        elif self.technique == "CA":
            ca = load_data.CA(self.fileName + ".txt", folder_save, model_pstat)
            sp.plotting.plot(
                ca.t,
                ca.i,
                show=False,
                fig=figNum,
                xlab="$t$ / s",
                ylab="$i$ / A",
                fileName=folder_save + "/" + self.fileName,
            )
        elif self.technique == "OCP":
            ocp = load_data.OCP(self.fileName + ".txt", folder_save, model_pstat)
            sp.plotting.plot(
                ocp.t,
                ocp.E,
                show=False,
                fig=figNum,
                xlab="$t$ / s",
                ylab="$E$ / V",
                fileName=folder_save + "/" + self.fileName,
            )
        plt.close()

    def message(self, start: bool = True) -> None:
        """Display a message indicating the start or end of the technique.

        Args:
            start: Whether the message indicates the start (True) or end (False) of the technique.
        """
        if start:
            print("----------\nStarting " + self.technique)
            if self.bpot:
                print("Running in bipotentiostat mode")
        else:
            print(self.technique + " finished\n----------\n")

    def bipot(self, E: float = -0.2, sens: float = 1e-6) -> None:
        """Enable bipotentiostat mode for the technique.

        Args:
            E: The potential for the second working electrode.
            sens: The sensitivity for the second working electrode.

        Note:
            Bipotentiostat mode is not available for OCP and EIS techniques.
        """
        if self.technique != "OCP" and self.technique != "EIS":
            if model_pstat == "chi760e":
                self.tech.bipot(E, sens)
                self.text = self.tech.text
                self.bpot = True
            if model_pstat == "chi1242b":
                self.tech.bipot(E, sens)
                self.text = self.tech.text
                self.bpot = True
            elif model_pstat == "emstatpico":
                self.tech.bipot(E, sens)
                self.text = self.tech.text
                self.bpot = True
        else:
            print(self.technique + " does not have bipotentiostat mode")


class CV(Technique):
    """Cyclic Voltammetry (CV) technique implementation.

    This class implements the Cyclic Voltammetry technique for various potentiostat models.

    Attributes:
        technique: Name of the technique ("CV").
        tech: The model-specific CV implementation object.

    Examples:
        ```python
        import hardpotato as hp

        # Setup potentiostat
        folder = "C:/Users/username/Experiments/data"
        hp.potentiostat.Setup('chi760e', 'C:/CHI/chi760e', folder)

        # Create and run CV
        cv = hp.potentiostat.CV(
            Eini=-0.5,     # Initial potential (V)
            Ev1=0.5,       # First vertex potential (V)
            Ev2=-0.5,      # Second vertex potential (V)
            Efin=0.0,      # Final potential (V)
            sr=0.1,        # Scan rate (V/s)
            dE=0.001,      # Potential increment (V)
            nSweeps=2,     # Number of sweeps
            sens=1e-6,     # Sensitivity (A/V)
            fileName="CV_test",
            header="CV Test"
        )
        cv.run()

        # Use bipotentiostat mode
        cv.bipot(E=0.2, sens=1e-6)
        cv.run()
        ```
    """

    def __init__(
        self,
        Eini: float = -0.2,
        Ev1: float = 0.2,
        Ev2: float = -0.2,
        Efin: float = -0.2,
        sr: float = 0.1,
        dE: float = 0.001,
        nSweeps: int = 2,
        sens: float = 1e-6,
        fileName: str = "CV",
        header: str = "CV",
        **kwargs: Any,
    ) -> None:
        """Initialize a Cyclic Voltammetry experiment.

        Args:
            Eini: Initial potential in V.
            Ev1: First vertex potential in V.
            Ev2: Second vertex potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            nSweeps: Number of sweeps.
            sens: Current sensitivity in A/V.
            fileName: Base name for the data files.
            header: Header for the data files.
            **kwargs: Additional parameters specific to the potentiostat model.
                      For example, 'mode' for emstatpico.
        """
        self.header = header
        if model_pstat == "chi601e":
            self.tech = chi601e.CV(
                Eini,
                Ev1,
                Ev2,
                Efin,
                sr,
                dE,
                nSweeps,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CV"
        if model_pstat == "chi760e":
            self.tech = chi760e.CV(
                Eini,
                Ev1,
                Ev2,
                Efin,
                sr,
                dE,
                nSweeps,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CV"
        elif model_pstat == "chi1205b":
            self.tech = chi1205b.CV(
                Eini,
                Ev1,
                Ev2,
                Efin,
                sr,
                dE,
                nSweeps,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CV"
        elif model_pstat == "chi1242b":
            self.tech = chi1242b.CV(
                Eini,
                Ev1,
                Ev2,
                Efin,
                sr,
                dE,
                nSweeps,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CV"
        elif model_pstat == "emstatpico":
            self.tech = emstatpico.CV(
                Eini,
                Ev1,
                Ev2,
                Efin,
                sr,
                dE,
                nSweeps,
                sens,
                folder_save,
                fileName,
                header,
                path_lib="",
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CV"
        else:
            print("Potentiostat model " + model_pstat + " does not have CV.")


class LSV(Technique):
    """Linear Sweep Voltammetry (LSV) technique implementation.

    This class implements the Linear Sweep Voltammetry technique for various potentiostat models.

    Attributes:
        technique: Name of the technique ("LSV").
        tech: The model-specific LSV implementation object.

    Examples:
        ```python
        import hardpotato as hp

        # Setup potentiostat
        folder = "C:/Users/username/Experiments/data"
        hp.potentiostat.Setup('chi760e', 'C:/CHI/chi760e', folder)

        # Create and run LSV
        lsv = hp.potentiostat.LSV(
            Eini=-0.2,     # Initial potential (V)
            Efin=0.5,      # Final potential (V)
            sr=0.05,       # Scan rate (V/s)
            dE=0.001,      # Potential increment (V)
            sens=1e-6,     # Sensitivity (A/V)
            fileName="LSV_test",
            header="LSV Test"
        )
        lsv.run()
        ```
    """

    def __init__(
        self,
        Eini: float = -0.2,
        Efin: float = 0.2,
        sr: float = 0.1,
        dE: float = 0.001,
        sens: float = 1e-6,
        fileName: str = "LSV",
        header: str = "LSV",
        **kwargs: Any,
    ) -> None:
        """Initialize a Linear Sweep Voltammetry experiment.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            sens: Current sensitivity in A/V.
            fileName: Base name for the data files.
            header: Header for the data files.
            **kwargs: Additional parameters specific to the potentiostat model.
        """
        self.header = header
        if model_pstat == "chi601e":
            self.tech = chi601e.LSV(
                Eini,
                Efin,
                sr,
                dE,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "LSV"
        if model_pstat == "chi760e":
            self.tech = chi760e.LSV(
                Eini,
                Efin,
                sr,
                dE,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "LSV"
        elif model_pstat == "chi1205b":
            self.tech = chi1205b.LSV(
                Eini,
                Efin,
                sr,
                dE,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "LSV"
        elif model_pstat == "chi1242b":
            self.tech = chi1242b.LSV(
                Eini,
                Efin,
                sr,
                dE,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "LSV"
        elif model_pstat == "emstatpico":
            self.tech = emstatpico.LSV(
                Eini,
                Efin,
                sr,
                dE,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "LSV"
        else:
            print("Potentiostat model " + model_pstat + " does not have LSV.")


class CA(Technique):
    """Chronoamperometry (CA) technique implementation.

    This class implements the Chronoamperometry technique for various potentiostat models.
    In CA, the potential is stepped from an initial value to a final value,
    and the current response is monitored over time.

    Attributes:
        technique: Name of the technique ("CA").
        tech: The model-specific CA implementation object.

    Examples:
        ```python
        import hardpotato as hp

        # Setup potentiostat
        folder = "C:/Users/username/Experiments/data"
        hp.potentiostat.Setup('emstatpico', None, folder)

        # Create and run CA
        ca = hp.potentiostat.CA(
            Estep=0.5,      # Step potential (V)
            dt=0.01,        # Time interval (s)
            ttot=10,        # Total time (s)
            sens=1e-6,      # Sensitivity (A/V)
            fileName="CA_test",
            header="CA Test"
        )
        ca.run()
        ```
    """

    def __init__(
        self,
        Estep: float = 0.2,
        dt: float = 0.001,
        ttot: float = 2,
        sens: float = 1e-6,
        fileName: str = "CA",
        header: str = "CA",
        **kwargs: Any,
    ) -> None:
        """Initialize a Chronoamperometry experiment.

        Args:
            Estep: Step potential in V.
            dt: Time interval in seconds.
            ttot: Total experiment time in seconds.
            sens: Current sensitivity in A/V.
            fileName: Base name for the data files.
            header: Header for the data files.
            **kwargs: Additional parameters specific to the potentiostat model.
        """
        self.header = header
        if model_pstat == "chi601e":
            self.tech = chi601e.CA(
                Estep, dt, ttot, sens, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CA"
        if model_pstat == "chi760e":
            self.tech = chi760e.CA(
                Estep, dt, ttot, sens, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CA"
        elif model_pstat == "chi1205b":
            self.tech = chi1205b.CA(
                Estep, dt, ttot, sens, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CA"
        elif model_pstat == "chi1242b":
            self.tech = chi1242b.CA(
                Estep, dt, ttot, sens, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CA"
        elif model_pstat == "emstatpico":
            self.tech = emstatpico.CA(
                Estep, dt, ttot, sens, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "CA"
        else:
            print("Potentiostat model " + model_pstat + " does not have CA.")


class OCP(Technique):
    """Open Circuit Potential (OCP) technique implementation.

    This class implements the Open Circuit Potential measurement technique for
    various potentiostat models. In OCP, the potential difference between the
    working and reference electrodes is measured without any current flow.

    Attributes:
        technique: Name of the technique ("OCP").
        tech: The model-specific OCP implementation object.

    Examples:
        ```python
        import hardpotato as hp

        # Setup potentiostat
        folder = "C:/Users/username/Experiments/data"
        hp.potentiostat.Setup('emstatpico', None, folder)

        # Create and run OCP
        ocp = hp.potentiostat.OCP(
            ttot=60,        # Total time (s)
            dt=0.1,         # Time interval (s)
            fileName="OCP_test",
            header="OCP Test"
        )
        ocp.run()
        ```
    """

    def __init__(
        self,
        ttot: float = 2,
        dt: float = 0.01,
        fileName: str = "OCP",
        header: str = "OCP",
        **kwargs: Any,
    ) -> None:
        """Initialize an Open Circuit Potential measurement.

        Args:
            ttot: Total experiment time in seconds.
            dt: Time interval in seconds.
            fileName: Base name for the data files.
            header: Header for the data files.
            **kwargs: Additional parameters specific to the potentiostat model.
        """
        self.header = header
        if model_pstat == "chi601e":
            self.tech = chi601e.OCP(
                ttot, dt, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "OCP"
        if model_pstat == "chi760e":
            self.tech = chi760e.OCP(
                ttot, dt, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "OCP"
        elif model_pstat == "chi1205b":
            self.tech = chi1205b.OCP(
                ttot, dt, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "OCP"
        elif model_pstat == "chi1242b":
            self.tech = chi1242b.OCP(
                ttot, dt, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "OCP"
        elif model_pstat == "emstatpico":
            self.tech = emstatpico.OCP(
                ttot, dt, folder_save, fileName, header, path_lib, **kwargs
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "OCP"
        else:
            print("Potentiostat model " + model_pstat + " does not have OCP.")


class NPV(Technique):
    """Normal Pulse Voltammetry (NPV) technique implementation.

    This class implements the Normal Pulse Voltammetry technique for CHI potentiostats.
    In NPV, the potential is pulsed from an initial value, with each successive pulse
    increasing in amplitude, and the current is measured at the end of each pulse.

    Attributes:
        technique: Name of the technique ("NPV").
        tech: The model-specific NPV implementation object.

    Examples:
        ```python
        import hardpotato as hp

        # Setup potentiostat
        folder = "C:/Users/username/Experiments/data"
        hp.potentiostat.Setup('chi760e', 'C:/CHI/chi760e', folder)

        # Create and run NPV
        npv = hp.potentiostat.NPV(
            Eini=0.2,       # Initial potential (V)
            Efin=-0.5,      # Final potential (V)
            dE=0.01,        # Potential increment (V)
            tsample=0.05,   # Sampling time (s)
            twidth=0.01,    # Pulse width (s)
            tperiod=0.2,    # Pulse period (s)
            sens=1e-6,      # Sensitivity (A/V)
            fileName="NPV_test",
            header="NPV Test"
        )
        npv.run()
        ```
    """

    def __init__(
        self,
        Eini: float = 0.5,
        Efin: float = -0.5,
        dE: float = 0.01,
        tsample: float = 0.1,
        twidth: float = 0.05,
        tperiod: float = 10,
        sens: float = 1e-6,
        fileName: str = "NPV",
        header: str = "NPV performed with CHI760",
        **kwargs: Any,
    ) -> None:
        """Initialize a Normal Pulse Voltammetry experiment.

        Args:
            Eini: Initial potential in V.
            Efin: Final potential in V.
            dE: Potential increment in V.
            tsample: Sampling time in seconds.
            twidth: Pulse width in seconds.
            tperiod: Pulse period in seconds.
            sens: Current sensitivity in A/V.
            fileName: Base name for the data files.
            header: Header for the data files.
            **kwargs: Additional parameters specific to the potentiostat model.
        """
        if model_pstat == "chi760e":
            self.tech = chi760e.NPV(
                Eini,
                Efin,
                dE,
                tsample,
                twidth,
                tperiod,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "NPV"
        elif model_pstat == "chi601e":
            self.tech = chi601e.NPV(
                Eini,
                Efin,
                dE,
                tsample,
                twidth,
                tperiod,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "NPV"
        else:
            print("Potentiostat model " + model_pstat + " does not have NPV.")


class EIS(Technique):
    """Electrochemical Impedance Spectroscopy (EIS) technique implementation.

    This class implements the Electrochemical Impedance Spectroscopy technique
    for supported potentiostat models. In EIS, a small sinusoidal potential
    perturbation is applied to the system across a range of frequencies, and
    the current response is measured to calculate impedance.

    Attributes:
        technique: Name of the technique ("EIS").
        tech: The model-specific EIS implementation object.

    Examples:
        ```python
        import hardpotato as hp

        # Setup potentiostat
        folder = "C:/Users/username/Experiments/data"
        hp.potentiostat.Setup('emstatpico', None, folder)

        # Create and run EIS
        eis = hp.potentiostat.EIS(
            ch=0,           # Channel (for emstatpico)
            Eini=0.0,       # Initial/DC potential (V)
            low_freq=1,     # Lowest frequency (Hz)
            high_freq=10000, # Highest frequency (Hz)
            amplitude=0.01, # Amplitude (V)
            sens=1e-6,      # Sensitivity (A/V)
            fileName="EIS_test",
            header="EIS Test"
        )
        eis.run()
        ```
    """

    def __init__(
        self,
        ch: int,
        Eini: float = 0,
        low_freq: float = 1,
        high_freq: float = 1000,
        amplitude: float = 0.01,
        sens: float = 1e-6,
        fileName: str = "EIS",
        header: str = "EIS",
        **kwargs: Any,
    ) -> None:
        """Initialize an Electrochemical Impedance Spectroscopy experiment.

        Args:
            ch: Channel number (relevant for emstatpico, typically 0 or 1).
            Eini: DC potential in V.
            low_freq: Lowest frequency in Hz.
            high_freq: Highest frequency in Hz.
            amplitude: Amplitude of the sinusoidal voltage perturbation in V.
            sens: Current sensitivity in A/V.
            fileName: Base name for the data files.
            header: Header for the data files.
            **kwargs: Additional parameters specific to the potentiostat model.
        """
        self.header = header
        if model_pstat == "chi760e":
            self.tech = chi760e.EIS(
                Eini,
                low_freq,
                high_freq,
                amplitude,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "EIS"
        elif model_pstat == "emstatpico":
            self.tech = emstatpico.EIS(
                Eini,
                ch,
                low_freq,
                high_freq,
                amplitude,
                sens,
                folder_save,
                fileName,
                header,
                path_lib,
                **kwargs,
            )
            Technique.__init__(self, text=self.tech.text, fileName=fileName)
            self.technique = "EIS"
        else:
            print("Potentiostat model " + model_pstat + " does not have EIS.")


if __name__ == "__main__":
    sens = 1e-8
    sr = [0.1, 0.2, 0.5]
    folder = "C:/Users/oliverrz/Desktop/Oliver/Data/220113_PythonMacros"

from typing import Any, Dict

import numpy as np

import hardpotato.pico_mscript as mscript


class Test:
    """Test class for the save_data module.

    This class is primarily used for testing and debugging purposes.
    """

    def __init__(self) -> None:
        """Initialize the Test class and print confirmation message."""
        print("Test from save_data module")


class Save:
    """Main class for saving experimental data to files.

    This class handles saving data from various electrochemical techniques
    to properly formatted text files.

    Attributes:
        fileName: Path to the file where data will be saved.
        data_array: Numpy array containing the formatted data to save.

    Examples:
        ```python
        import hardpotato as hp
        import numpy as np

        # Create data array (typically comes from a potentiostat)
        data = {...}  # Data dictionary from Emstat Pico

        # Save CV data
        save = hp.save_data.Save(
            data,
            "C:/Data/experiment.txt",
            "Cyclic Voltammetry Experiment",
            "emstatpico",
            "CV"
        )
        ```
    """

    def __init__(
        self,
        data: Dict[str, Any],
        fileName: str,
        header: str,
        model: str,
        technique: str,
        bpot: bool = False,
    ) -> None:
        """Initialize the Save class and save data to file.

        Args:
            data: Dictionary containing the experimental data.
            fileName: Path to the file where data will be saved.
            header: Text header to include at the top of the file.
            model: Potentiostat model identifier ('chi760e', 'emstatpico', etc.).
            technique: Type of electrochemical technique ('CV', 'LSV', 'CA', 'OCP', 'EIS').
            bpot: Whether the data was collected using bipotentiostat mode.
        """
        self.fileName = fileName
        self.data_array: np.ndarray = np.array([])

        if technique == "CV" or technique == "LSV":
            header = header + "\nt/s, E/V, i/A\n"
            self.data_array = CV(fileName, data, model, bpot).save()
        elif technique == "IT" or technique == "CA":
            header = header + "\nt/s, E/V, i/A\n"
            self.data_array = IT(fileName, data, model, bpot).save()
        elif technique == "OCP":
            header = header + "\nt/s, E/V\n"
            self.data_array = OCP(fileName, data, model).save()
        elif technique == "EIS":
            header = header + "\nF, Real, Imaginary\n"
            self.data_array = EIS(fileName, data, model).save()

        np.savetxt(fileName, self.data_array, delimiter=",", header=header)


class CV:
    """Class for formatting and saving Cyclic Voltammetry (CV) data.

    This class handles extraction and organization of CV data for saving to file.

    Attributes:
        fileName: Path to the file where data will be saved.
        data: Dictionary containing the experimental data.
        model: Potentiostat model identifier.
        bpot: Whether the data was collected using bipotentiostat mode.
    """

    def __init__(
        self, fileName: str, data: Dict[str, Any], model: str, bpot: bool
    ) -> None:
        """Initialize the CV data formatter.

        Args:
            fileName: Path to the file where data will be saved.
            data: Dictionary containing the experimental data.
            model: Potentiostat model identifier ('chi760e', 'emstatpico', etc.).
            bpot: Whether the data was collected using bipotentiostat mode.
        """
        self.fileName = fileName
        self.data = data
        self.model = model
        self.bpot = bpot

    def save(self) -> np.ndarray:
        """Format the CV data for saving.

        Returns:
            np.ndarray: Formatted array containing the CV data:
                - Column 0: Time (s)
                - Column 1: Potential (V)
                - Column 2: Current (A)
                - Column 3: Current at second WE (A) if using bipotentiostat mode
        """
        data_array = np.array([])

        if self.model == "emstatpico":
            t = mscript.get_values_by_column(self.data, 0)
            E = mscript.get_values_by_column(self.data, 1)
            i = mscript.get_values_by_column(self.data, 2)
            data_array = np.array([t, E, i]).T

            if self.bpot:
                i2 = mscript.get_values_by_column(self.data, 3)
                data_array = np.array([t, E, i, i2]).T

        return data_array


class IT:
    """Class for formatting and saving Chronoamperometry (CA) data.

    This class handles extraction and organization of CA data for saving to file.
    CA is also known as I vs T (IT) data.

    Attributes:
        fileName: Path to the file where data will be saved.
        data: Dictionary containing the experimental data.
        model: Potentiostat model identifier.
        bpot: Whether the data was collected using bipotentiostat mode.
    """

    def __init__(
        self, fileName: str, data: Dict[str, Any], model: str, bpot: bool
    ) -> None:
        """Initialize the IT data formatter.

        Args:
            fileName: Path to the file where data will be saved.
            data: Dictionary containing the experimental data.
            model: Potentiostat model identifier ('chi760e', 'emstatpico', etc.).
            bpot: Whether the data was collected using bipotentiostat mode.
        """
        self.fileName = fileName
        self.data = data
        self.model = model
        self.bpot = bpot

    def save(self) -> np.ndarray:
        """Format the IT data for saving.

        Returns:
            np.ndarray: Formatted array containing the CA data:
                - Column 0: Time (s)
                - Column 1: Potential (V)
                - Column 2: Current (A)
                - Column 3: Current at second WE (A) if using bipotentiostat mode
        """
        data_array = np.array([])

        if self.model == "emstatpico":
            t = mscript.get_values_by_column(self.data, 0)
            E = mscript.get_values_by_column(self.data, 1)
            i = mscript.get_values_by_column(self.data, 2)
            data_array = np.array([t, E, i]).T

            if self.bpot:
                i2 = mscript.get_values_by_column(self.data, 3)
                data_array = np.array([t, E, i, i2]).T

        return data_array


class OCP:
    """Class for formatting and saving Open Circuit Potential (OCP) data.

    This class handles extraction and organization of OCP data for saving to file.

    Attributes:
        fileName: Path to the file where data will be saved.
        data: Dictionary containing the experimental data.
        model: Potentiostat model identifier.
    """

    def __init__(self, fileName: str, data: Dict[str, Any], model: str) -> None:
        """Initialize the OCP data formatter.

        Args:
            fileName: Path to the file where data will be saved.
            data: Dictionary containing the experimental data.
            model: Potentiostat model identifier ('chi760e', 'emstatpico', etc.).
        """
        self.fileName = fileName
        self.data = data
        self.model = model

    def save(self) -> np.ndarray:
        """Format the OCP data for saving.

        Returns:
            np.ndarray: Formatted array containing the OCP data:
                - Column 0: Time (s)
                - Column 1: Potential (V)
        """
        data_array = np.array([])

        if self.model == "emstatpico":
            t = mscript.get_values_by_column(self.data, 0)
            E = mscript.get_values_by_column(self.data, 1)
            data_array = np.array([t, E]).T

        return data_array


class EIS:
    """Class for formatting and saving Electrochemical Impedance Spectroscopy (EIS) data.

    This class handles extraction and organization of EIS data for saving to file.

    Attributes:
        fileName: Path to the file where data will be saved.
        data: Dictionary containing the experimental data.
        model: Potentiostat model identifier.
    """

    def __init__(self, fileName: str, data: Dict[str, Any], model: str) -> None:
        """Initialize the EIS data formatter.

        Args:
            fileName: Path to the file where data will be saved.
            data: Dictionary containing the experimental data.
            model: Potentiostat model identifier ('chi760e', 'emstatpico', etc.).
        """
        self.fileName = fileName
        self.data = data
        self.model = model

    def save(self) -> np.ndarray:
        """Format the EIS data for saving.

        Returns:
            np.ndarray: Formatted array containing the EIS data:
                - Column 0: Frequency (Hz)
                - Column 1: Real part of impedance (Ω)
                - Column 2: Imaginary part of impedance (Ω)
        """
        data_array = np.array([])

        if self.model == "emstatpico":
            freq = mscript.get_values_by_column(self.data, 0)
            z_re = mscript.get_values_by_column(self.data, 1)
            z_im = mscript.get_values_by_column(self.data, 2)
            data_array = np.array([freq, z_re, z_im]).T

        return data_array

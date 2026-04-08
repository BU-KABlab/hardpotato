from typing import Any, Dict

import numpy as np

import hardpotato.pico_mscript as mscript


class Test:
    """Test class for the save_data module."""

    def __init__(self) -> None:
        print("Test from save_data module")


class Save:
    """Main class for saving experimental data to files."""

    def __init__(
        self,
        data: Dict[str, Any],
        fileName: str,
        header: str,
        model: str,
        technique: str,
        bpot: bool = False,
    ) -> None:
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
            header = header + "\nFreq/Hz, Real/Ohm, Imag/Ohm\n"
            self.data_array = EIS(fileName, data, model).save()
        np.savetxt(fileName, self.data_array, delimiter=",", header=header)


class CV:
    """Class for formatting and saving Cyclic Voltammetry (CV) data."""

    def __init__(
        self, fileName: str, data: Dict[str, Any], model: str, bpot: bool
    ) -> None:
        self.fileName = fileName
        self.data = data
        self.model = model
        self.bpot = bpot

    def save(self) -> np.ndarray:
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
    """Class for formatting and saving Chronoamperometry (CA) data."""

    def __init__(
        self, fileName: str, data: Dict[str, Any], model: str, bpot: bool
    ) -> None:
        self.fileName = fileName
        self.data = data
        self.model = model
        self.bpot = bpot

    def save(self) -> np.ndarray:
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
    """Class for formatting and saving Open Circuit Potential (OCP) data."""

    def __init__(self, fileName: str, data: Dict[str, Any], model: str) -> None:
        self.fileName = fileName
        self.data = data
        self.model = model

    def save(self) -> np.ndarray:
        data_array = np.array([])
        if self.model == "emstatpico":
            t = mscript.get_values_by_column(self.data, 0)
            E = mscript.get_values_by_column(self.data, 1)
            data_array = np.array([t, E]).T
        return data_array


class EIS:
    """Class for formatting and saving EIS data."""

    def __init__(self, fileName: str, data: Dict[str, Any], model: str) -> None:
        self.fileName = fileName
        self.data = data
        self.model = model

    def save(self) -> np.ndarray:
        data_array = np.array([])
        if self.model == "emstatpico":
            freq = mscript.get_values_by_column(self.data, 0)
            real = mscript.get_values_by_column(self.data, 1)
            imag = mscript.get_values_by_column(self.data, 2)
            data_array = np.array([freq, real, imag]).T
        return data_array

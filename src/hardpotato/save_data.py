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
        else:
            # Handle custom MethodScript data
            mscript_data = MSCRIPT(fileName, data, model).save()
            if mscript_data.size > 0:
                # Extract headers from the first row
                column_headers = mscript_data[0].tolist()
                header = header + "\n" + ", ".join(column_headers) + "\n"
                # Get numeric data (skip headers row)
                self.data_array = mscript_data[1:].astype(float)
            else:
                self.data_array = np.array([])
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


class MSCRIPT:
    """Class for parsing and saving custom MethodScript data.

    This class handles data from user-defined MethodScript experiments,
    which may have varying column structures.
    """

    def __init__(self, fileName: str, data: Any, model: str) -> None:
        self.fileName = fileName
        self.data = data
        self.model = model

    def _parse_mscript_data_to_array(self) -> np.ndarray:
        """Parse MethodScript data into a numpy array with headers.

        Returns:
            numpy array with column headers as first row.
        """
        # Collect all unique column headers across all curves
        column_types = {}
        time_column_name = None

        # First pass: identify all unique column types and find the time column
        for curve in self.data:
            for package in curve:
                for col in package:
                    col_key = f"{col.type.name}/{col.type.unit}"
                    if col_key not in column_types:
                        column_types[col_key] = {
                            "name": col.type.name,
                            "unit": col.type.unit,
                            "index": len(column_types),
                        }
                    # Identify time column (usually has 's' as unit)
                    if col.type.unit == "s" and col.type.name.lower() in ["time", "t"]:
                        time_column_name = col_key

        # Prepare the column headers
        column_headers = list(column_types.keys())

        # If we found a time column, make sure it's the first one
        if time_column_name and time_column_name in column_headers:
            column_headers.remove(time_column_name)
            column_headers.insert(0, time_column_name)

        # Second pass: extract data values
        all_data_points = []

        for curve in self.data:
            for package in curve:
                data_point = [np.nan] * len(column_headers)
                for col in package:
                    col_key = f"{col.type.name}/{col.type.unit}"
                    if col_key in column_headers:
                        col_pos = column_headers.index(col_key)
                        data_point[col_pos] = col.value
                all_data_points.append(data_point)

        # Convert to numpy array
        if all_data_points:
            data_array = np.array(all_data_points)

            # Sort by time if time column exists
            if time_column_name:
                time_idx = column_headers.index(time_column_name)
                valid_time_mask = ~np.isnan(data_array[:, time_idx])
                if np.any(valid_time_mask):
                    valid_rows = data_array[valid_time_mask]
                    sorted_indices = np.argsort(valid_rows[:, time_idx])
                    valid_rows = valid_rows[sorted_indices]
                    data_array[valid_time_mask] = valid_rows

            # Add column headers as the first row
            data_array = np.vstack((column_headers, data_array))
            return data_array
        else:
            return np.array([column_headers])

    def save(self) -> np.ndarray:
        """Save MethodScript data.

        Returns:
            numpy array with parsed data.
        """
        if self.model == "emstatpico":
            return self._parse_mscript_data_to_array()
        else:
            return np.array([])

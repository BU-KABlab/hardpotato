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
        else:
            header = header
            mscript_data = MSCRIPT(fileName, data, model).save()

            # Extract headers from the first row for the header text
            column_headers = mscript_data[0].tolist()
            header = header + "\n" + " ".join(column_headers) + "\n"

            # Get only the numeric data (skip headers row) and ensure it's numeric type
            self.data_array = mscript_data[1:].astype(float).T.transpose()

        try:
            np.savetxt(fileName, self.data_array, delimiter=",", header=header)
        except Exception as e:
            print("Error saving file: ", e)


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


class MSCRIPT:
    """ """

    def __init__(self, fileName, data, model):
        self.fileName = fileName
        self.data = data
        self.model = model

    def _parse_mscript_data_to_array(self):
        """
        Parse MethodScript data from multiple techniques into a single array with proper column headers.
        Data is combined and sorted by time when possible.
        """
        # Collect all unique column headers across all curves
        column_types = {}  # Dictionary to store unique column types by name+unit
        time_column_name = None  # Track which column is the time column

        # First pass: identify all unique column types and find the time column
        for curve_idx, curve in enumerate(self.data):
            for package in curve:
                for col_idx, col in enumerate(package):
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

        # Prepare the column headers (sorted list)
        column_headers = list(column_types.keys())

        # If we found a time column, make sure it's the first one
        if time_column_name and time_column_name in column_headers:
            column_headers.remove(time_column_name)
            column_headers.insert(0, time_column_name)

        # Second pass: extract data values for each column type from each curve
        all_data_points = []

        for curve_idx, curve in enumerate(self.data):
            for package_idx, package in enumerate(curve):
                # Create a data point with NaN for all columns
                data_point = [np.nan] * len(column_headers)

                # Extract values for columns present in this package
                for col_idx, col in enumerate(package):
                    col_key = f"{col.type.name}/{col.type.unit}"
                    if col_key in column_headers:
                        col_pos = column_headers.index(col_key)
                        # Extract the actual value from the MScriptVar
                        value = (
                            col.value
                        )  # You might need a different way to extract the value
                        data_point[col_pos] = value

                all_data_points.append(data_point)

        # Convert to numpy array
        if all_data_points:
            data_array = np.array(all_data_points)

            # Sort by time if time column exists
            if time_column_name:
                time_idx = column_headers.index(time_column_name)
                # Only sort rows with valid time values
                valid_time_mask = ~np.isnan(data_array[:, time_idx])
                if np.any(valid_time_mask):
                    valid_rows = data_array[valid_time_mask]
                    sorted_indices = np.argsort(valid_rows[:, time_idx])
                    valid_rows = valid_rows[sorted_indices]

                    # Replace the valid rows in the original array
                    data_array[valid_time_mask] = valid_rows

            # Add column headers as the first row
            data_array = np.vstack((column_headers, data_array))
            return data_array
        else:
            # Return empty array with headers if no data points
            return np.array([column_headers])

    def save(self):
        if self.model == "emstatpico":
            data_array = self._parse_mscript_data_to_array()
        else:
            # Handle other models if needed
            data_array = np.array([])
        return data_array

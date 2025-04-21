import numpy as np

import hardpotato.pico_mscript as mscript


class Test:
    """ """

    def __init__(self):
        print("Test from save_data module")


class Save:
    """ """

    def __init__(self, data, fileName, header, model, technique, bpot=0):
        self.fileName = fileName
        self.data_array = 0
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
    """ """

    def __init__(self, fileName, data, model, bpot):
        self.fileName = fileName
        self.data = data
        self.model = model
        self.bpot = bpot

    def save(self):
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
    """ """

    def __init__(self, fileName, data, model, bpot):
        self.fileName = fileName
        self.data = data
        self.model = model
        self.bpot = bpot

    def save(self):
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
    """ """

    def __init__(self, fileName, data, model):
        self.fileName = fileName
        self.data = data
        self.model = model

    def save(self):
        if self.model == "emstatpico":
            t = mscript.get_values_by_column(self.data, 0)
            E = mscript.get_values_by_column(self.data, 1)
            # i = mscript.get_values_by_column(self.data,2)
            data_array = np.array([t, E]).T
        return data_array


class EIS:
    """ """

    def __init__(self, fileName, data, model):
        self.fileName = fileName
        self.data = data
        self.model = model

    def save(self):
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

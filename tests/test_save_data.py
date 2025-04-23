import os
from unittest.mock import patch

import numpy as np

import hardpotato.save_data as save_data


class TestSave:
    def test_save_cv_chi(self, temp_folder, sample_cv_data):
        """Test saving CV data for CHI potentiostat."""
        # Setup
        filepath = os.path.join(temp_folder, "test_cv.txt")
        header = "Test CV"
        model = "chi760e"
        technique = "CV"

        # Create sample structured array
        dtype = [("E", float), ("i", float)]
        data = np.zeros(len(sample_cv_data["E"]), dtype=dtype)
        data["E"] = sample_cv_data["E"]
        data["i"] = sample_cv_data["i"]

        # Call function
        with patch("builtins.open", create=True) as mock_open:
            save_data.Save(data, filepath, header, model, technique)
            mock_open.assert_called_once_with(filepath, "w")

    def test_save_cv_emstatpico(self, temp_folder):
        """Test saving CV data for EmStat Pico."""
        # Setup
        filepath = os.path.join(temp_folder, "test_cv.txt")
        header = "Test CV"
        model = "emstatpico"
        technique = "CV"

        # Create sample emstat pico data (structured array)
        dtype = [("aa", float), ("ab", float), ("ba", float)]
        data = np.array(
            [(0.0, 0.2, 0.000020), (0.01, 0.2, 0.000019), (0.02, 0.2, 0.000018)],
            dtype=dtype,
        )

        # Call function
        with patch("builtins.open", create=True) as mock_open:
            save_data.Save(data, filepath, header, model, technique)
            mock_open.assert_called_once_with(filepath, "w")

    def test_save_ca(self, temp_folder, sample_ca_data):
        """Test saving CA data."""
        # Setup
        filepath = os.path.join(temp_folder, "test_ca.txt")
        header = "Test CA"
        model = "chi760e"
        technique = "CA"

        # Create sample structured array
        dtype = [("t", float), ("i", float)]
        data = np.zeros(len(sample_ca_data["t"]), dtype=dtype)
        data["t"] = sample_ca_data["t"]
        data["i"] = sample_ca_data["i"]

        # Call function
        with patch("builtins.open", create=True) as mock_open:
            save_data.Save(data, filepath, header, model, technique)
            mock_open.assert_called_once_with(filepath, "w")

    def test_save_ocp(self, temp_folder, sample_ocp_data):
        """Test saving OCP data."""
        # Setup
        filepath = os.path.join(temp_folder, "test_ocp.txt")
        header = "Test OCP"
        model = "chi760e"
        technique = "OCP"

        # Create sample structured array
        dtype = [("t", float), ("E", float)]
        data = np.zeros(len(sample_ocp_data["t"]), dtype=dtype)
        data["t"] = sample_ocp_data["t"]
        data["E"] = sample_ocp_data["E"]

        # Call function
        with patch("builtins.open", create=True) as mock_open:
            save_data.Save(data, filepath, header, model, technique)
            mock_open.assert_called_once_with(filepath, "w")

    def test_save_bipot(self, temp_folder, sample_cv_data):
        """Test saving data in bipotentiostat mode."""
        # Setup
        filepath = os.path.join(temp_folder, "test_bipot.txt")
        header = "Test Bipot CV"
        model = "chi760e"
        technique = "CV"

        # Create sample structured array with an additional current column
        dtype = [("E", float), ("i", float), ("i2", float)]
        data = np.zeros(len(sample_cv_data["E"]), dtype=dtype)
        data["E"] = sample_cv_data["E"]
        data["i"] = sample_cv_data["i"]
        data["i2"] = sample_cv_data["i"] * 0.5  # Second WE current

        # Call function
        with patch("builtins.open", create=True) as mock_open:
            save_data.Save(data, filepath, header, model, technique, bpot=True)
            mock_open.assert_called_once_with(filepath, "w")

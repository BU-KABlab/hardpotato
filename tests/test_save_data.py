import os

import numpy as np
import pytest

import hardpotato.save_data as save_data


class TestSave:
    def test_save_cv_chi(self, temp_folder, sample_cv_data):
        """Test saving CV data for CHI potentiostat.
        
        Note: CHI data saving is not implemented in save_data.py,
        so this test verifies the class can be instantiated without error
        when data_array is empty.
        """
        filepath = os.path.join(temp_folder, "test_cv.txt")
        header = "Test CV"
        model = "chi760e"
        technique = "CV"

        # Create sample structured array
        dtype = [("E", float), ("i", float)]
        data = np.zeros(len(sample_cv_data["E"]), dtype=dtype)
        data["E"] = sample_cv_data["E"]
        data["i"] = sample_cv_data["i"]

        # For CHI model, the save returns empty array since it's not implemented
        # This test verifies no exception is raised
        save_data.Save(data, filepath, header, model, technique)
        
        # Verify file was created
        assert os.path.exists(filepath)

    def test_save_ca(self, temp_folder, sample_ca_data):
        """Test saving CA data."""
        filepath = os.path.join(temp_folder, "test_ca.txt")
        header = "Test CA"
        model = "chi760e"
        technique = "CA"

        # Create sample structured array
        dtype = [("t", float), ("i", float)]
        data = np.zeros(len(sample_ca_data["t"]), dtype=dtype)
        data["t"] = sample_ca_data["t"]
        data["i"] = sample_ca_data["i"]

        # For CHI model, the save returns empty array since it's not implemented
        save_data.Save(data, filepath, header, model, technique)
        
        # Verify file was created
        assert os.path.exists(filepath)

    def test_save_ocp(self, temp_folder, sample_ocp_data):
        """Test saving OCP data."""
        filepath = os.path.join(temp_folder, "test_ocp.txt")
        header = "Test OCP"
        model = "chi760e"
        technique = "OCP"

        # Create sample structured array
        dtype = [("t", float), ("E", float)]
        data = np.zeros(len(sample_ocp_data["t"]), dtype=dtype)
        data["t"] = sample_ocp_data["t"]
        data["E"] = sample_ocp_data["E"]

        # For CHI model, the save returns empty array since it's not implemented
        save_data.Save(data, filepath, header, model, technique)
        
        # Verify file was created
        assert os.path.exists(filepath)

    def test_save_bipot(self, temp_folder, sample_cv_data):
        """Test saving data in bipotentiostat mode."""
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

        # For CHI model, the save returns empty array since it's not implemented
        save_data.Save(data, filepath, header, model, technique, bpot=True)
        
        # Verify file was created
        assert os.path.exists(filepath)


class TestCV:
    def test_cv_init(self):
        """Test CV class initialization."""
        data = {"test": "data"}
        cv = save_data.CV("test.txt", data, "emstatpico", False)
        assert cv.fileName == "test.txt"
        assert cv.model == "emstatpico"
        assert cv.bpot is False


class TestIT:
    def test_it_init(self):
        """Test IT class initialization."""
        data = {"test": "data"}
        it = save_data.IT("test.txt", data, "emstatpico", False)
        assert it.fileName == "test.txt"
        assert it.model == "emstatpico"
        assert it.bpot is False


class TestOCP:
    def test_ocp_init(self):
        """Test OCP class initialization."""
        data = {"test": "data"}
        ocp = save_data.OCP("test.txt", data, "emstatpico")
        assert ocp.fileName == "test.txt"
        assert ocp.model == "emstatpico"


class TestEIS:
    def test_eis_init(self):
        """Test EIS class initialization."""
        data = {"test": "data"}
        eis = save_data.EIS("test.txt", data, "emstatpico")
        assert eis.fileName == "test.txt"
        assert eis.model == "emstatpico"

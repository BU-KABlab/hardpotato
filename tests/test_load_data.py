import os

import hardpotato.load_data as load_data


class TestLoadData:
    def test_cv_chi_load(self, temp_folder):
        """Test loading CV data for CHI potentiostat."""
        file_content = """Test CV

Potential/V,Current/A
-0.500000,0.000001
-0.490000,0.000002
-0.480000,0.000003
-0.470000,0.000004
"""
        # Write actual file
        filepath = os.path.join(temp_folder, "test_cv.txt")
        with open(filepath, "w") as f:
            f.write(file_content)

        cv = load_data.CV("test_cv.txt", temp_folder, "chi760e")

        assert hasattr(cv, "E")
        assert hasattr(cv, "i")
        assert len(cv.E) == 4
        assert cv.E[0] == -0.5

    def test_cv_emstatpico_load(self, temp_folder):
        """Test loading CV data for EmStat Pico."""
        file_content = """0.000000,0.200000,0.000020
0.010000,0.200000,0.000019
0.020000,0.200000,0.000018
"""
        # Write actual file
        filepath = os.path.join(temp_folder, "test_cv.txt")
        with open(filepath, "w") as f:
            f.write(file_content)

        cv = load_data.CV("test_cv.txt", temp_folder, "emstatpico")

        assert hasattr(cv, "t")
        assert hasattr(cv, "E")
        assert hasattr(cv, "i")
        assert len(cv.E) == 3
        assert cv.E[0] == 0.2

    def test_lsv_load(self, temp_folder):
        """Test loading LSV data."""
        file_content = """Test LSV

Potential/V,Current/A
-0.500000,0.000001
-0.490000,0.000002
-0.480000,0.000003
"""
        # Write actual file
        filepath = os.path.join(temp_folder, "test_lsv.txt")
        with open(filepath, "w") as f:
            f.write(file_content)

        lsv = load_data.LSV("test_lsv.txt", temp_folder, "chi760e")

        assert hasattr(lsv, "E")
        assert hasattr(lsv, "i")
        assert len(lsv.E) == 3
        assert lsv.E[0] == -0.5

    def test_ca_load(self, temp_folder):
        """Test loading CA data."""
        file_content = """Test CA

Time/sec,Current/A
0.000000,0.000010
0.010000,0.000009
0.020000,0.000008
"""
        # Write actual file
        filepath = os.path.join(temp_folder, "test_ca.txt")
        with open(filepath, "w") as f:
            f.write(file_content)

        ca = load_data.CA("test_ca.txt", temp_folder, "chi760e")

        assert hasattr(ca, "t")
        assert hasattr(ca, "i")
        assert len(ca.t) == 3
        assert ca.t[0] == 0.0

    def test_ocp_load(self, temp_folder):
        """Test loading OCP data."""
        file_content = """Test OCP

Time/sec,Potential/V
0.000000,0.250000
0.010000,0.248000
0.020000,0.246000
"""
        # Write actual file
        filepath = os.path.join(temp_folder, "test_ocp.txt")
        with open(filepath, "w") as f:
            f.write(file_content)

        ocp = load_data.OCP("test_ocp.txt", temp_folder, "chi760e")

        assert hasattr(ocp, "t")
        assert hasattr(ocp, "E")
        assert len(ocp.t) == 3
        assert ocp.t[0] == 0.0
        # Note: y values are negated in the read() method
        assert ocp.E[0] == -0.25

    def test_bipot_load(self, temp_folder):
        """Test loading data in bipotentiostat mode."""
        file_content = """Test Bipot CV

Potential/V,Current/A,Current2/A
-0.500000,0.000001,0.0000005
-0.490000,0.000002,0.0000010
-0.480000,0.000003,0.0000015
"""
        # Write actual file
        filepath = os.path.join(temp_folder, "test_bipot.txt")
        with open(filepath, "w") as f:
            f.write(file_content)

        cv = load_data.CV("test_bipot.txt", temp_folder, "chi760e")

        assert hasattr(cv, "E")
        assert hasattr(cv, "i")
        assert len(cv.E) == 3

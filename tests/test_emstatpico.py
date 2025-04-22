from unittest.mock import patch

import pytest

import hardpotato.emstatpico as emstatpico


class TestInfo:
    def test_init(self):
        """Test Info initialization."""
        info = emstatpico.Info()
        assert hasattr(info, "E_min")
        assert hasattr(info, "E_max")
        assert hasattr(info, "i_min")
        assert hasattr(info, "i_max")

    def test_specifications(self):
        """Test specifications method."""
        with patch("hardpotato.emstatpico.print") as mock_print:
            info = emstatpico.Info()
            info.specifications()
            assert mock_print.called

    def test_limits_within_range(self):
        """Test limits method with value within range."""
        info = emstatpico.Info()
        # Test with value inside range
        result = info.limits(0, -2, 2, "test_param", "V")
        assert result is True

    def test_limits_outside_range(self):
        """Test limits method with value outside range."""
        info = emstatpico.Info()
        # Test with value outside range
        with patch("hardpotato.emstatpico.print") as mock_print:
            with pytest.raises(ValueError):
                info.limits(3, -2, 2, "test_param", "V")


class TestCV:
    def test_init(self):
        """Test CV initialization."""
        cv = emstatpico.CV(
            Eini=-0.5,
            Ev1=0.5,
            Ev2=-0.5,
            Efin=-0.5,
            sr=0.1,
            dE=0.001,
            nSweeps=2,
            sens=1e-6,
            folder="test_folder",
            fileName="test_cv",
            header="Test CV",
        )

        assert cv.Eini == -500  # Check conversion to mV
        assert cv.Ev1 == 500
        assert cv.Ev2 == -500
        assert cv.Efin == -500
        assert cv.sr == 100
        assert cv.dE == 1
        assert cv.nSweeps == 2

    def test_validate(self):
        """Test validation of CV parameters."""
        cv = emstatpico.CV(
            Eini=-0.5,
            Ev1=0.5,
            Ev2=-0.5,
            Efin=-0.5,
            sr=0.1,
            dE=0.001,
            nSweeps=2,
            sens=1e-6,
            folder="test_folder",
            fileName="test_cv",
            header="Test CV",
        )
        with patch.object(emstatpico.Info, "limits", return_value=True):
            cv.validate(-0.5, 0.5, -0.5, -0.5, 0.1, 0.001, 2, 1e-6)

    def test_bipot(self):
        """Test bipotentiostat mode configuration."""
        cv = emstatpico.CV()
        cv.Eini = -500
        cv.validate(-0.5, 0.5, -0.5, -0.5, 0.1, 0.001, 2, 1e-6)
        with patch.object(emstatpico.Info, "limits", return_value=True):
            cv.bipot(0.3, 1e-6)
            assert "set_pgstat_chan 1" in cv.text
            assert "set_e 300m" in cv.text  # 0.3V converted to 300mV


class TestLSV:
    def test_init(self):
        """Test LSV initialization."""
        lsv = emstatpico.LSV(
            Eini=-0.5,
            Efin=0.5,
            sr=0.1,
            dE=0.001,
            sens=1e-6,
            folder="test_folder",
            fileName="test_lsv",
            header="Test LSV",
        )

        assert lsv.Eini == -500  # Check conversion to mV
        assert lsv.Efin == 500
        assert lsv.sr == 0.1
        assert lsv.dE == 0.001
        assert lsv.sens == 1e-6

    def test_validate(self):
        """Test validation of LSV parameters."""
        lsv = emstatpico.LSV()
        with patch.object(emstatpico.Info, "limits", return_value=True):
            result = lsv.validate(-0.5, 0.5, 0.1, 0.001, 1e-6)
            assert result is True

    def test_bipot(self):
        """Test bipotentiostat mode configuration."""
        lsv = emstatpico.LSV()
        lsv.Eini = -500
        lsv.validate(-0.5, 0.5, 0.1, 0.001, 1e-6)
        with patch.object(emstatpico.Info, "limits", return_value=True):
            lsv.bipot(0.3, 1e-6)
            assert "set_pgstat_chan 1" in lsv.text
            assert "set_e 300m" in lsv.text  # 0.3V converted to 300mV


class TestCA:
    def test_init(self):
        """Test CA initialization."""
        ca = emstatpico.CA(
            Estep=0.3,
            dt=0.01,
            ttot=1,
            sens=1e-6,
            folder="test_folder",
            fileName="test_ca",
            header="Test CA",
        )

        assert ca.Estep == 300  # Check conversion to mV
        assert ca.dt == 0.01
        assert ca.ttot == 1
        assert ca.sens == 1e-6

    def test_validate(self):
        """Test validation of CA parameters."""
        ca = emstatpico.CA(
            Estep=0.3,
            dt=0.01,
            ttot=1,
            sens=1e-6,
            folder="test_data",
            fileName="test_ca",
            header="Test CA",
        )
        with patch.object(emstatpico.Info, "limits", return_value=True):
            result = ca.validate(0.3, 0.01, 1, 1e-6)
            assert result is True

    def test_bipot(self):
        """Test bipotentiostat mode configuration."""
        ca = emstatpico.CA()
        ca.Estep = 300
        ca.validate(0.3, 0.01, 1, 1e-6)
        with patch.object(emstatpico.Info, "limits", return_value=True):
            ca.bipot(0.3, 1e-6)
            assert "set_pgstat_chan 1" in ca.text
            assert "set_e 300m" in ca.text  # 0.3V converted to 300mV


class TestOCP:
    def test_init(self):
        """Test OCP initialization."""
        ocp = emstatpico.OCP(
            ttot=5,
            dt=0.01,
            folder="test_folder",
            fileName="test_ocp",
            header="Test OCP",
        )

        assert ocp.ttot == 5
        assert ocp.dt == 0.01

    def test_validate(self):
        """Test validation of OCP parameters."""
        ocp = emstatpico.OCP(
            ttot=5,
            dt=0.01,
            folder="test_folder",
            fileName="test_ocp",
            header="Test OCP",
        )
        ocp.validate(5, 10)


class TestEIS:
    def test_init(self):
        """Test EIS initialization."""
        eis = emstatpico.EIS(
            Edc=0.2,
            ch=0,
            fstart=1,
            fend=1000,
            amp=0.01,
            sens=1e-6,
            folder="test_folder",
            fileName="test_eis",
            header="Test EIS",
        )

        assert eis.Edc == 200  # Check conversion to mV
        assert eis.ch == 0
        assert eis.fstart == 1
        assert eis.fend == 1000
        assert eis.amp == 10  # Check conversion to mV
        assert eis.sens == 1e-6

    def test_validate(self):
        """Test validation of EIS parameters."""
        eis = emstatpico.EIS()
        with patch.object(emstatpico.Info, "limits", return_value=True):
            result = eis.validate(0.2, 0, 1, 1000, 0.01, 1e-6)
            assert result is True

    def test_generate_script(self):
        """Test script generation."""
        eis = emstatpico.EIS()
        eis.validate(0.2, 0, 1, 1000, 0.01, 1e-6)
        eis.generate_script()
        assert "var p" in eis.text  # Basic check that script contains expected content


class TestCustomMethodScript:
    def test_init_with_path(self):
        """Test CustomMethodScript initialization with file path."""
        test_content = "var c\nset_pgstat_mode 2\nmeas_loop_lsv ba 500m -500m 100m 10m\npause_ms 100\nendloop\n"
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                test_content
            )
            ms = emstatpico.CustomMethodScript("test/path/script.mscr")
            assert ms.text == test_content

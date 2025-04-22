import os
from unittest.mock import MagicMock, patch

import hardpotato.potentiostat as potentiostat


class TestSetup:
    def test_init(self):
        """Test Setup initialization."""
        with patch("hardpotato.potentiostat.print") as mock_print:
            setup = potentiostat.Setup(
                "chi760e", "path/to/chi", "/data/folder", verbose=1
            )
            assert potentiostat.model_pstat == "chi760e"
            assert potentiostat.path_lib == "path/to/chi"
            assert potentiostat.folder_save == "/data/folder"
            assert mock_print.called

    def test_info(self):
        """Test displaying potentiostat info."""
        with patch("hardpotato.potentiostat.print") as mock_print:
            potentiostat.model_pstat = "chi760e"
            potentiostat.path_lib = "path/to/chi"
            potentiostat.folder_save = "/data/folder"
            potentiostat.Setup(verbose=1)
            assert mock_print.called

    def test_not_printing_info(self):
        """Test not printing info when verbose is 0."""
        with patch("hardpotato.potentiostat.print") as mock_print:
            potentiostat.Setup(verbose=0)
            assert not mock_print.called


class TestTechnique:
    def test_init(self):
        """Test Technique initialization."""
        tech = potentiostat.Technique(text="test text", fileName="test_file")
        assert tech.text == "test text"
        assert tech.fileName == "test_file"
        assert tech.technique == "Technique"
        assert tech.bpot is False

    def test_write_to_file_chi(self, temp_folder):
        """Test writing macro to file for CHI potentiostats."""
        potentiostat.model_pstat = "chi760e"
        potentiostat.folder_save = temp_folder
        tech = potentiostat.Technique(text="test text", fileName="test_file")
        with patch("builtins.open") as mock_open:
            tech.writeToFile()
            mock_open.assert_called_once_with(
                os.path.join(temp_folder, "test_file.mcr"), "wb"
            )

    def test_write_to_file_emstat(self, temp_folder):
        """Test writing script to file for EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = temp_folder
        tech = potentiostat.Technique(text="test text", fileName="test_file")
        with patch("builtins.open") as mock_open:
            tech.writeToFile()
            mock_open.assert_called_once_with(
                os.path.join(temp_folder, "test_file.mscr"), "wb"
            )

    def test_run_chi(self, temp_folder, mock_subprocess_run):
        """Test running experiment with CHI potentiostat."""
        potentiostat.model_pstat = "chi760e"
        potentiostat.folder_save = temp_folder
        potentiostat.path_lib = "/path/to/chi.exe"

        with patch.object(potentiostat.Technique, "writeToFile"):
            with patch.object(potentiostat.Technique, "message"):
                with patch.object(potentiostat.Technique, "plot"):
                    tech = potentiostat.Technique(
                        text="test text", fileName="test_file"
                    )
                    tech.run()
                    mock_subprocess_run.assert_called_once()

    def test_run_emstat(self, temp_folder, mock_instrument, sample_emstatpico_result):
        """Test running experiment with EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = temp_folder
        potentiostat.port_ = "/dev/ttyUSB0"

        with patch.object(potentiostat.Technique, "writeToFile"):
            with patch.object(potentiostat.Technique, "message"):
                with patch("hardpotato.pico_serial.Serial"):
                    with patch("hardpotato.potentiostat.mscript.parse_result_lines"):
                        with patch("hardpotato.potentiostat.save_data.Save"):
                            mock_instrument.readlines_until_end.return_value = (
                                sample_emstatpico_result
                            )

                            tech = potentiostat.Technique(
                                text="test text", fileName="test_file"
                            )
                            tech.run()

                            mock_instrument.send_script.assert_called_once()

    def test_bipot(self):
        """Test setting bipotentiostat mode."""
        potentiostat.model_pstat = "emstatpico"

        # Mock tech attribute with bipot method
        mock_tech = MagicMock()
        tech = potentiostat.Technique(text="test text", fileName="test_file")
        tech.tech = mock_tech
        tech.technique = "CV"

        tech.bipot(E=0.3, sens=1e-7)

        mock_tech.bipot.assert_called_once_with(0.3, 1e-7)


class TestCV:
    def test_init_emstatpico(self):
        """Test CV initialization for EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = "/test/folder"

        with patch("hardpotato.emstatpico.CV") as mock_cv:
            mock_instance = MagicMock()
            mock_cv.return_value = mock_instance
            mock_instance.text = "mock CV text"

            cv = potentiostat.CV(Eini=-0.4, Ev1=0.6, header="Test CV")

            mock_cv.assert_called_once()
            assert cv.technique == "CV"
            assert cv.header == "Test CV"

    def test_init_chi760e(self):
        """Test CV initialization for CHI760E."""
        potentiostat.model_pstat = "chi760e"
        potentiostat.folder_save = "/test/folder"
        potentiostat.path_lib = "/path/to/chi.exe"

        with patch("hardpotato.chi760e.CV") as mock_cv:
            mock_instance = MagicMock()
            mock_cv.return_value = mock_instance
            mock_instance.text = "mock CV text"

            cv = potentiostat.CV(Eini=-0.4, Ev1=0.6, header="Test CV")

            mock_cv.assert_called_once()
            assert cv.technique == "CV"
            assert cv.header == "Test CV"


class TestLSV:
    def test_init_emstatpico(self):
        """Test LSV initialization for EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = "/test/folder"

        with patch("hardpotato.emstatpico.LSV") as mock_lsv:
            mock_instance = MagicMock()
            mock_lsv.return_value = mock_instance
            mock_instance.text = "mock LSV text"

            lsv = potentiostat.LSV(Eini=-0.4, Efin=0.6, header="Test LSV")

            mock_lsv.assert_called_once()
            assert lsv.technique == "LSV"
            assert lsv.header == "Test LSV"


class TestCA:
    def test_init_emstatpico(self):
        """Test CA initialization for EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = "/test/folder"

        with patch("hardpotato.emstatpico.CA") as mock_ca:
            mock_instance = MagicMock()
            mock_ca.return_value = mock_instance
            mock_instance.text = "mock CA text"

            ca = potentiostat.CA(Estep=0.3, ttot=5, header="Test CA")

            mock_ca.assert_called_once()
            assert ca.technique == "CA"
            assert ca.header == "Test CA"


class TestOCP:
    def test_init_emstatpico(self):
        """Test OCP initialization for EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = "/test/folder"

        with patch("hardpotato.emstatpico.OCP") as mock_ocp:
            mock_instance = MagicMock()
            mock_ocp.return_value = mock_instance
            mock_instance.text = "mock OCP text"

            ocp = potentiostat.OCP(ttot=10, header="Test OCP")

            mock_ocp.assert_called_once()
            assert ocp.technique == "OCP"
            assert ocp.header == "Test OCP"


class TestEIS:
    def test_init_emstatpico(self):
        """Test EIS initialization for EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = "/test/folder"

        with patch("hardpotato.emstatpico.EIS") as mock_eis:
            mock_instance = MagicMock()
            mock_eis.return_value = mock_instance
            mock_instance.text = "mock EIS text"

            eis = potentiostat.EIS(ch=0, Eini=0.2, header="Test EIS")

            mock_eis.assert_called_once()
            assert eis.technique == "EIS"
            assert eis.header == "Test EIS"


class TestMethodScript:
    def test_init_emstatpico(self):
        """Test MethodScript initialization for EmStat Pico."""
        potentiostat.model_pstat = "emstatpico"
        potentiostat.folder_save = "/test/folder"

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                "mock script"
            )
            with patch("hardpotato.emstatpico.CustomMethodScript") as mock_ms:
                mock_instance = MagicMock()
                mock_ms.return_value = mock_instance
                mock_instance.text = "mock script text"

                filepath = "/test/folder/test_script.mscr"
                ms = potentiostat.MethodScript(filepath=filepath)

                assert ms.filepath == filepath

class Test:
    """ """

    def __init__(self):
        print("Test from Emstat Pico translator")


class Info:
    """
    Info class for Emstat Pico

    Establishes the limits for the Emstat Pico potentiostat.
    This class is used to validate the parameters for the Emstat Pico potentiostat.

    Parameters:
        model: Model of the potentiostat. Options are "low_range" (default) or "high_range"
    """

    def __init__(self, model="low_range"):
        self.tech = ["CV", "CA", "LSV", "OCP", "EIS"]
        self.options = [
            "mode (low_speed, high_speed, max_range)",
        ]
        self.model = (
            model.lower()
        )  # Convert to lowercase for case-insensitive comparison

        # Set specifications based on model
        if self.model == "high_range" or self.model == "hr":
            # High Range specifications
            self.E_min = -6.0  # V
            self.E_max = 6.0  # V
            self.i_min = 0.0000001  # A (100 nA)
            self.i_max = 0.1  # A (100 mA)
            self.compliance_voltage = 8.0  # V
        else:
            # Low Range specifications (default)
            self.E_min = -3.0  # V
            self.E_max = 3.0  # V
            self.i_min = 0.000000001  # A (1 nA)
            self.i_max = 0.01  # A (10 mA)
            self.compliance_voltage = 5.0  # V

        # EIS frequency range (same for both models)
        self.freq_min = 0.00000001  # Hz (10 µHz)
        self.freq_max = 200000  # Hz (200 kHz)

        # SR values for CV/LSV
        self.sr_min = 0.000001  # V/s
        self.sr_max = 10.0  # V/s

        # Potential step
        self.dE_min = 0.0001  # V (0.1 mV)
        self.dE_max = 0.25  # V (250 mV)

        # Time parameters
        self.dt_min = 0.0001  # s (0.1 ms)
        self.dt_max = 300  # s (5 min)
        self.ttot_min = 0.001  # s (1 ms)
        self.ttot_max = 86400  # s (24 hours)

    def limits(self, val, low, high, label, units):
        if val < low or val > high:
            raise ValueError(
                label
                + " should be between "
                + str(low)
                + " "
                + units
                + " and "
                + str(high)
                + " "
                + units
                + ". Received "
                + str(val)
                + " "
                + units
            )
        else:
            return True

    def specifications(self):
        print("Model: PalmSens Emstat Pico")
        print(f"Model type: {self.model.upper()}")
        print(f"Potential range: {self.E_min} V to {self.E_max} V")
        print(f"Current range: {self.i_min} A to {self.i_max} A")
        print(f"Compliance voltage: {self.compliance_voltage} V")
        print(f"EIS frequency range: {self.freq_min} Hz to {self.freq_max} Hz")
        print("Techiques available:", self.tech)
        print("Options available:", self.options)


def get_mode(val):
    if val == "low_speed":
        return 2
    elif val == "high_speed":
        return 3
    elif val == "max_range":
        return 4
    else:
        return 4


class CV:
    """
    Emstat Pico CV class

    Parameters:
        Eini: Initial potential (V)
        Ev1: First potential (V)
        Ev2: Second potential (V)
        Efin: Final potential (V)
        sr: Sampling rate (Hz)
        dE: Potential step size (V)
        nSweeps: Number of sweeps
        sens: Sensitivity (A/V)
        folder: Folder to save data
        fileName: Name of the file to save data
        header: Header for the data file
        path_lib: Path to the library (optional)
        **kwargs: Additional parameters

    **kwargs:
        mode # 'low_speed', 'high_speed', 'max_range'
    """

    def __init__(
        self,
        Eini,
        Ev1,
        Ev2,
        Efin,
        sr,
        dE,
        nSweeps,
        sens,
        folder,
        fileName,
        header,
        path_lib=None,
        **kwargs,
    ):
        """
        Potential based variables need to be changed to mV int(Eini*100).
        For some reason Pico does not accept not having prefix
        """
        self.Eini = int(Eini * 1000)
        self.Ev1 = int(Ev1 * 1000)
        self.Ev2 = int(Ev2 * 1000)
        self.Efin = int(Efin * 1000)
        self.sr = int(sr * 1000)
        self.dE = int(dE * 1000)
        self.nSweeps = nSweeps
        self.text = ""

        if "mode" in kwargs:
            self.mode = kwargs.get("mode")
            self.mode = get_mode(self.mode)
        else:
            self.mode = 4  # Defaults to max_range

        self.validate(Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens)

        self.ini = "e\nvar c\nvar p\nvar a\n"
        self.pre_body = (
            "set_pgstat_mode "
            + str(self.mode)
            + "\nset_autoranging ba 100n 5m"
            + "\nset_e "
            + str(self.Eini)
            + "m\ncell_on\nwait 2\ntimer_start"
        )
        self.body = (
            "\nmeas_loop_cv p c "
            + str(self.Eini)
            + "m "
            + str(self.Ev1)
            + "m "
            + str(self.Ev2)
            + "m "
            + str(self.dE)
            + "m "
            + str(self.sr)
            + "m nscans("
            + str(self.nSweeps - 1)
            + ")\n\tpck_start\n\ttimer_get a"
            + "\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_end\nendloop\n"
            + "on_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body

    def validate(self, Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens):
        # Check if global emstat_model_type is defined
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model=model_type)
        else:
            info = Info()

        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Ev1, info.E_min, info.E_max, "Ev1", "V")
        info.limits(Ev2, info.E_min, info.E_max, "Ev2", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")

    def bipot(self, E, sens):
        # Validate bipot:
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model=model_type)
        else:
            info = Info()

        info.limits(E, info.E_min, info.E_max, "E2", "V")

        E = int(E * 1000)
        self.pre_body = (
            "var b\nset_pgstat_chan 1"
            + "\nset_pgstat_mode 5"
            + "\nset_poly_we_mode 0"
            + "\nset_e "
            + str(E)
            + "m\nset_autoranging ba 100n 5m"
            + "\nset_pgstat_chan 0\nset_pgstat_mode 2"
            + "\nset_autoranging ba 100n 5m\nset_e "
            + str(self.Eini)
            + "m\ntimer_start\ncell_on"
        )
        self.body = (
            "\nmeas_loop_cv p c "
            + str(self.Eini)
            + "m "
            + str(self.Ev1)
            + "m "
            + str(self.Ev2)
            + "m "
            + str(self.dE)
            + "m "
            + str(self.sr)
            + "m nscans("
            + str(self.nSweeps)
            + ") poly_we(1 b)\n\t"
            + "pck_start\n\ttimer_get a"
            + "\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_add b\n\t"
            + "pck_end\nendloop\non_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body
        # print(self.text)


class CA:
    """
    Emstat Pico CA class

    Parameters:
        Estep: Potential step (V)
        dt: Time step (s)
        ttot: Total time (s)
        sens: Sensitivity (A/V)
        folder: Folder to save data
        fileName: Name of the file to save data
        header: Header for the data file
        path_lib: Path to the library (optional)
        **kwargs: Additional parameters

    **kwargs:
        mode @ 'low_speed', 'high_speed', 'max_range'
    """

    def __init__(
        self, Estep, dt, ttot, sens, folder, fileName, header, path_lib=None, **kwargs
    ):
        """
        Potential based variables need to be changed to mV int(Eini*100).

        """
        self.Estep = int(Estep * 1000)
        self.dt = int(dt * 1000)
        self.ttot = int(ttot * 1000)
        self.text = ""

        if "mode" in kwargs:
            self.mode = kwargs.get("mode")
            self.mode = get_mode(self.mode)
        else:
            self.mode = 4  # Defaults to max_range

        self.validate(Estep, dt, ttot, sens)

        self.ini = "e\nvar p\nvar c\nvar a\n"
        self.pre_body = (
            "set_pgstat_mode "
            + str(self.mode)
            + "\nset_autoranging ba 100n 5m"
            + "\nset_e "
            + str(self.Estep)
            + "m\ncell_on\ntimer_start"
        )
        self.body = (
            "\nmeas_loop_ca p c "
            + str(self.Estep)
            + "m "
            + str(self.dt)
            + "m "
            + str(self.ttot)
            + "m\n\tpck_start\n\ttimer_get a\n\t"
            + "pck_add a\n\t"
            + "pck_add p\n\tpck_add c\n\tpck_end\n\tendloop"
            + "\non_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body

    def validate(self, Estep, dt, ttot, sens):
        """
        Validate CA parameters

        Parameters:
            Estep: Potential step (V)
            dt: Time step (s)
            ttot: Total time (s)
            sens: Sensitivity (A/V)

        Raises:
            ValueError: If Estep, dt, ttot, or sens are out of range.

        """
        # Check if global emstat_model_type is defined
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model_type)
        else:
            info = Info()

        info.limits(Estep, info.E_min, info.E_max, "Estep", "V")
        info.limits(dt, info.dt_min, info.dt_max, "dt", "s")
        info.limits(ttot, info.ttot_min, info.ttot_max, "ttot", "s")

    def bipot(self, E, sens):
        """
        Establish a bipotentiostat mode for CA

        This method sets the EmStat Pico to operate in bipotentiostat mode, allowing for simultaneous control of two electrodes.

        Parameters:
            E: Potential (V)
            sens: Sensitivity (A/V)

        Raises:
            ValueError: If E is out of range.
        """
        # Check if global emstat_model_type is defined
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model=model_type)
        else:
            info = Info()

        info.limits(E, info.E_min, info.E_max, "E2", "V")

        E = int(E * 1000)
        self.pre_body = (
            "var b\nset_pgstat_chan 1"
            + "\nset_pgstat_mode 5"
            + "\nset_poly_we_mode 0"
            + "\nset_e "
            + str(E)
            + "m\nset_autoranging ba 100n 5m"
            + "\nset_pgstat_chan 0\nset_pgstat_mode 2"
            + "\nset_autoranging ba 100n 5m\nset_e "
            + str(self.Estep)
            + "m\ntimer_start\ncell_on"
        )
        self.body = (
            "\nmeas_loop_ca p c "
            + str(self.Estep)
            + "m "
            + str(self.dt)
            + "m "
            + str(self.ttot)
            + "m poly_we(1 b)\n\t"
            + "pck_start\n\ttimer_get a"
            + "\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_add b\n\t"
            + "pck_end\nendloop\non_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body

        pass


class LSV:
    """
    Emstat Pico LSV class

    NOTE: SI units are converted to mV, mA, mS for the EmStat Pico.

    Parameters:
        Eini: Initial potential (V)
        Efin: Final potential (V)
        sr: Sampling rate (Hz)
        dE: Potential step size (V)
        sens: Sensitivity (A/V)
        folder: Folder to save data
        fileName: Name of the file to save data
        header: Header for the data file
        path_lib: Path to the library (optional)
        **kwargs: Additional parameters

    **kwargs:
        mode # 'low_speed', 'high_speed', 'max_range'
    """

    def __init__(
        self,
        Eini,
        Efin,
        sr,
        dE,
        sens,
        folder,
        fileName,
        header,
        path_lib=None,
        **kwargs,
    ):
        self.Eini = int(Eini * 1000)
        self.Efin = int(Efin * 1000)
        self.sr = int(sr * 1000)
        self.dE = int(dE * 1000)
        self.text = ""

        if "mode" in kwargs:
            self.mode = kwargs.get("mode")
            self.mode = get_mode(self.mode)
        else:
            self.mode = 4  # Defaults to max_range

        self.validate(Eini, Efin, sr, dE, sens)

        self.ini = "e\nvar c\nvar p\nvar a\n"
        self.pre_body = (
            "set_pgstat_mode "
            + str(self.mode)
            + "\nset_autoranging ba 100n 5m"
            + "\nset_e "
            + str(self.Eini)
            + "m\ncell_on\ntimer_start"
        )
        self.body = (
            "\nmeas_loop_lsv p c "
            + str(self.Eini)
            + "m "
            + str(self.Efin)
            + "m "
            + str(self.dE)
            + "m "
            + str(self.sr)
            + "m\n\tpck_start\n\ttimer_get a"
            + "\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_end\nendloop\n"
            + "on_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body

    def bipot(self, E, sens):
        """Establish a bipotentiostat mode for LSV
        This method sets the EmStat Pico to operate in bipotentiostat mode, allowing for simultaneous control of two electrodes.
        Parameters:
            E: Potential (V)
            sens: Sensitivity (A/V)
        Raises:
            ValueError: If E is out of range.
        """
        # Check if global emstat_model_type is defined
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model=model_type)
        else:
            info = Info()

        info.limits(E, info.E_min, info.E_max, "E2", "V")

        E = int(E * 1000)
        self.pre_body = (
            "var b\nset_pgstat_chan 1"
            + "\nset_pgstat_mode 5"
            + "\nset_poly_we_mode 0"
            + "\nset_e "
            + str(E)
            + "m\nset_autoranging ba 100n 5m"
            + "\nset_pgstat_chan 0\nset_pgstat_mode 2"
            + "\nset_autoranging ba 100n 5m\nset_e "
            + str(self.Eini)
            + "m\ntimer_start\ncell_on"
        )
        self.body = (
            "\nmeas_loop_lsv p c "
            + str(self.Eini)
            + "m "
            + str(self.Efin)
            + "m "
            + str(self.dE)
            + "m "
            + str(self.sr)
            + "m poly_we(1 b)\n\t"
            + "pck_start\n\ttimer_get a"
            + "\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_add b\n\t"
            + "pck_end\nendloop\non_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body
        # print(self.text)

    def validate(self, Eini, Efin, sr, dE, sens):
        """
        Validate LSV parameters

        Parameters:
            Eini: Initial potential (V)
            Efin: Final potential (V)
            sr: Sampling rate (Hz)
            dE: Potential step size (V)
            sens: Sensitivity (A/V)

        Raises:
            ValueError: If Eini, Efin, sr, dE, or sens are out of range.

        """
        # Check if global emstat_model_type is defined
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model=model_type)
        else:
            info = Info()

        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        info.limits(sr, info.sr_min, info.sr_max, "sr", "V/s")
        info.limits(dE, info.dE_min, info.dE_max, "dE", "V")


class OCP:
    """
    Emstat Pico OCP class

    Parameters:
        ttot: Total time (s)
        dt: Time step (s)
        folder: Folder to save data
        fileName: Name of the file to save data
        header: Header for the data file
        path_lib: Path to the library (optional)
        **kwargs: Additional parameters

    """

    def __init__(self, ttot, dt, folder, fileName, header, path_lib=None, **kwargs):
        self.dt = int(dt * 1000)
        self.ttot = int(ttot * 1000)
        self.text = ""

        self.validate(ttot, dt)

        self.ini = "e\nvar p\nvar a\n"
        self.pre_body = "set_pgstat_mode 4\ncell_off\ntimer_start\n"
        self.body = (
            "meas_loop_ocp p "
            + str(self.dt)
            + "m "
            + str(self.ttot)
            + "m "
            + "\n\tpck_start\n\ttimer_get a\n\tpck_add a\n\tpck_add p"
            + "\n\tpck_end\nendloop\non_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body

    def validate(self, ttot, dt):
        """
        Validate OCP parameters

        Parameters:
            ttot: Total time (s)
            dt: Time step (s)

        Raises:
            ValueError: If ttot or dt are out of range.
        """
        # Check if global emstat_model_type is defined
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model=model_type)
        else:
            info = Info()

        info.limits(dt, info.dt_min, info.dt_max, "dt", "s")
        info.limits(ttot, info.ttot_min, info.ttot_max, "ttot", "s")


class EIS:
    """
    Pending:
    * Validate parameters
    """

    def __init__(
        self,
        Eini,
        ch,
        low_freq,
        high_freq,
        amplitude,
        sens,
        folder,
        fileName,
        header,
        path_lib,
        **kwargs,
    ):
        self.Eini = int(Eini * 1000)
        self.ch = ch
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.amplitude = amplitude
        self.sens = sens
        self.text = ""
        self.path_lib = path_lib
        self.validate(Eini, ch, low_freq, high_freq, amplitude, sens)

        if ch == 0:
            self.text = "e\nvar h\nvar r\nvar j\nset_pgstat_chan 1\nset_pgstat_mode 0\nset_pgstat_chan 0\nset_pgstat_mode 3\nset_max_bandwidth 200k\nset_range_minmax da 0 0\nset_range ba 2950u\nset_autoranging ba 2950u 2950u\nset_range ab 4200m\nset_autoranging ab 4200m 4200m\nset_e 0\ncell_on\nmeas_loop_eis h r j 100m 200k 100 31 0\n  pck_start\n    pck_add h\n    pck_add r\n    pck_add j\n  pck_end\nendloop\non_finished:\n  cell_off\n\n"
        elif ch == 1:
            self.text = "e\nvar h\nvar r\nvar j\nset_pgstat_chan 0\nset_pgstat_mode 0\nset_pgstat_chan 1\nset_pgstat_mode 3\nset_max_bandwidth 200k\nset_range_minmax da 0 0\nset_range ba 2950u\nset_autoranging ba 2950n 2950u\nset_range ab 4200m\nset_autoranging ab 4200m 4200m\nset_e 0\ncell_on\nmeas_loop_eis h r j 100m 200k 100 34 0\n  pck_start\n    pck_add h\n    pck_add r\n    pck_add j\n  pck_end\nendloop\non_finished:\n  cell_off\n\n"

    def validate(self, Edc, ch, fstart, fend, amp, sens):
        """
        Validate EIS parameters

        Parameters:
            Edc: DC potential (V)
            ch: Channel number
            fstart: Start frequency (Hz)
            fend: End frequency (Hz)
            amp: AC amplitude (V)
            sens: Sensitivity (A/V)

        Raises:
            ValueError: If any parameters are out of range
        """
        # Check if global emstat_model_type is defined
        import hardpotato.potentiostat as potentiostat

        if hasattr(potentiostat, "emstat_model_type"):
            model_type = potentiostat.emstat_model_type
            info = Info(model=model_type)
        else:
            info = Info()

        info.limits(Edc, info.E_min, info.E_max, "Edc", "V")
        info.limits(fstart, info.freq_min, info.freq_max, "fstart", "Hz")
        info.limits(fend, info.freq_min, info.freq_max, "fend", "Hz")

        return True


class CustomMethodScript:
    """
    CustomMethodScript class

    Paramters:
            filepath: filepath to a user authored MethoScript file.

    Raises:
            FileNotFoundError: If the script file is not found.
            Exception: If there is an error loading the script.
    """

    def __init__(self, filepath):
        self.text = ""
        self.load_script(filepath)

    def load_script(self, filepath):
        try:
            with open(filepath, "r") as file:
                script = file.read()
            self.text = script
        except FileNotFoundError:
            raise FileNotFoundError(f"Script file {filepath} not found.")
        except Exception as e:
            raise Exception(f"Error loading script: {e}")

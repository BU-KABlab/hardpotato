from typing import Any, List, Optional


class Test:
    """Test class for verifying the Emstat Pico translator module.

    This class is primarily used for testing and debugging purposes.
    """

    def __init__(self) -> None:
        """Initialize the Test class and print confirmation message."""
        print("Test from Emstat Pico translator")


class Info:
    """Information class for the Emstat Pico potentiostat.

    Contains specifications and validation functionality for the
    Emstat Pico potentiostat, including available techniques, options, and
    parameter limits.

    Attributes:
        tech: List of available techniques.
        options: List of available options.
        E_min: Minimum potential value in V.
        E_max: Maximum potential value in V.
    """

    def __init__(self) -> None:
        """Initialize the Info class with Emstat Pico specifications."""
        self.tech: List[str] = ["CV", "CA", "LSV", "OCP", "EIS"]
        self.options: List[str] = [
            "mode (low_speed, high_speed, max_range)",
        ]

        self.E_min: float = -1.7  # Minimum potential in V
        self.E_max: float = 2  # Maximum potential in V
        # self.sr_min = 0.000001
        # self.sr_max = 10
        # self.dE_min =
        # self.sr_min =
        # self.dt_min =
        # self.dt_max =
        # self.ttot_min =
        # self.ttot_max =

    def limits(
        self, val: float, low: float, high: float, label: str, units: str
    ) -> None:
        """Check if a value is within specified limits.

        Args:
            val: The value to check.
            low: The lower limit.
            high: The upper limit.
            label: Name of the parameter being checked.
            units: Units of the parameter being checked.

        Raises:
            Exception: If the value is outside the specified limits.
        """
        if val < low or val > high:
            raise Exception(
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

    def specifications(self) -> None:
        """Print the specifications of the Emstat Pico potentiostat."""
        print("Model: PalmSens Emstat Pico (emstatpico)")
        print("Techiques available:", self.tech)
        print("Options available:", self.options)


def get_mode(val: str) -> int:
    """Convert mode string to corresponding integer value.

    Args:
        val: Mode string ('low_speed', 'high_speed', or 'max_range')

    Returns:
        int: Integer representing the mode (2 for low_speed, 3 for high_speed,
             4 for max_range, defaults to 4)
    """
    if val == "low_speed":
        return 2
    elif val == "high_speed":
        return 3
    elif val == "max_range":
        return 4
    else:
        return 4


class CV:
    """Cyclic Voltammetry (CV) technique for the Emstat Pico potentiostat.

    This class handles the creation of CV method scripts for the Emstat Pico.

    Attributes:
        text: The complete method script as a string.

    Examples:
        ```python
        import hardpotato as hp

        # Setup Emstat Pico
        folder = "C:/Users/username/Experiments/data"
        hp.potentiostat.Setup('emstatpico', None, folder)

        # Define parameters
        Eini = -0.5    # V, initial potential
        Ev1 = 0.5      # V, first vertex potential
        Ev2 = -0.5     # V, second vertex potential
        Efin = 0.0     # V, final potential
        sr = 0.1       # V/s, scan rate
        dE = 0.001     # V, potential increment
        nSweeps = 2    # number of sweeps
        sens = 1e-6    # A/V, current sensitivity
        fileName = "CV_test"
        header = "CV"

        # Create and run CV
        cv = hp.potentiostat.CV(Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens, fileName, header)
        cv.run()
        ```

    Additional options:
        mode: Operation mode ('low_speed', 'high_speed', or 'max_range')
    """

    def __init__(
        self,
        Eini: float,
        Ev1: float,
        Ev2: float,
        Efin: float,
        sr: float,
        dE: float,
        nSweeps: int,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a CV experiment for the Emstat Pico.

        Args:
            Eini: Initial potential in V.
            Ev1: First vertex potential in V.
            Ev2: Second vertex potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            nSweeps: Number of sweeps.
            sens: Current sensitivity in A/V.
            folder: Path to save data.
            fileName: Base name for data files.
            header: Header for data files.
            path_lib: Library path (not used for Emstat Pico).
            **kwargs: Additional options:
                mode: Operation mode ('low_speed', 'high_speed', 'max_range')

        Note:
            Potential values are automatically converted to mV integers for the Pico.
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

    def validate(
        self,
        Eini: float,
        Ev1: float,
        Ev2: float,
        Efin: float,
        sr: float,
        dE: float,
        nSweeps: int,
        sens: float,
    ) -> None:
        """Validate the parameters for the CV experiment.

        Args:
            Eini: Initial potential in V.
            Ev1: First vertex potential in V.
            Ev2: Second vertex potential in V.
            Efin: Final potential in V.
            sr: Scan rate in V/s.
            dE: Potential increment in V.
            nSweeps: Number of sweeps.
            sens: Current sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside the specified limits.
        """
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Ev1, info.E_min, info.E_max, "Ev1", "V")
        info.limits(Ev2, info.E_min, info.E_max, "Ev2", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        # info.limits(sr, info.sr_min, info.sr_max, 'sr', 'V/s')
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

    def bipot(self, E: float, sens: float) -> None:
        """Configure the bipotentiostat mode for the CV experiment.

        Args:
            E: Second working electrode potential in V.
            sens: Current sensitivity in A/V.

        Raises:
            Exception: If any parameter is outside the specified limits.
        """
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E2", "V")
        # info.limits(sens2, info.sens_min, info.sens_max, 'sens', 'A/V')

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
    **kwargs:
        mode @ 'low_speed', 'high_speed', 'max_range'
    """

    def __init__(
        self, Estep, dt, ttot, sens, folder, fileName, header, path_lib=None, **kwargs
    ) -> None:
        """ """
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

    def validate(self, Estep: float, dt: float, ttot: float, sens: float) -> None:
        info = Info()
        info.limits(Estep, info.E_min, info.E_max, "Estep", "V")
        # info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        # info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')

    def bipot(self, E: float, sens: float) -> None:
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E2", "V")
        # info.limits(sens2, info.sens_min, info.sens_max, 'sens2', 'A/V')

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
    **kwargs:
        mode # 'low_speed', 'high_speed', 'max_range'
    """

    def __init__(
        self,
        Eini: float,
        Efin: float,
        sr: float,
        dE: float,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
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

    def bipot(self, E: float, sens: float) -> None:
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, "E2", "V")
        # info.limits(sens2, info.sens_min, info.sens_max, 'sens', 'A/V')

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

    def validate(
        self, Eini: float, Efin: float, sr: float, dE: float, sens: float
    ) -> None:
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, "Eini", "V")
        info.limits(Efin, info.E_min, info.E_max, "Efin", "V")
        # info.limits(sr, info.sr_min, info.sr_max, 'sr', 'V/s')
        # info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        # info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')


class OCP:
    """ """

    def __init__(
        self,
        ttot: float,
        dt: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        dt = int(dt * 1000)
        ttot = int(ttot * 1000)
        self.text = ""

        self.validate(ttot, dt)

        self.ini = "e\nvar p\nvar a\n"
        self.pre_body = "set_pgstat_mode 4\ncell_off\ntimer_start\n"
        self.body = (
            "meas_loop_ocp p "
            + str(dt)
            + "m "
            + str(ttot)
            + "m "
            + "\n\tpck_start\n\ttimer_get a\n\tpck_add a\n\tpck_add p"
            + "\n\tpck_end\nendloop\non_finished:\ncell_off\n\n"
        )
        self.text = self.ini + self.pre_body + self.body

    def validate(self, ttot: float, dt: float) -> None:
        """Validate the parameters for the OCP experiment.

        Args:
            ttot: Total time in s.
            dt: Time increment in s.

        """

        _ = Info()
        # info.limits(dt, info.dt_min, info.dt_max, "dt", "s")
        # info.limits(ttot, info.ttot_min, info.ttot_max, "ttot", "s")


class EIS:
    """
    Pending:
    * Validate parameters
    """

    def __init__(
        self,
        Eini: float,
        ch: int,
        low_freq: float,
        high_freq: float,
        amplitude: float,
        sens: float,
        folder: str,
        fileName: str,
        header: str,
        path_lib: Optional[str],
        **kwargs: Any,
    ) -> None:
        if ch == 0:
            self.text = "e\nvar h\nvar r\nvar j\nset_pgstat_chan 1\nset_pgstat_mode 0\nset_pgstat_chan 0\nset_pgstat_mode 3\nset_max_bandwidth 200k\nset_range_minmax da 0 0\nset_range ba 2950u\nset_autoranging ba 2950u 2950u\nset_range ab 4200m\nset_autoranging ab 4200m 4200m\nset_e 0\ncell_on\nmeas_loop_eis h r j 100m 200k 100 31 0\n  pck_start\n    pck_add h\n    pck_add r\n    pck_add j\n  pck_end\nendloop\non_finished:\n  cell_off\n\n"
        elif ch == 1:
            self.text = "e\nvar h\nvar r\nvar j\nset_pgstat_chan 0\nset_pgstat_mode 0\nset_pgstat_chan 1\nset_pgstat_mode 3\nset_max_bandwidth 200k\nset_range_minmax da 0 0\nset_range ba 2950u\nset_autoranging ba 2950n 2950u\nset_range ab 4200m\nset_autoranging ab 4200m 4200m\nset_e 0\ncell_on\nmeas_loop_eis h r j 100m 200k 100 34 0\n  pck_start\n    pck_add h\n    pck_add r\n    pck_add j\n  pck_end\nendloop\non_finished:\n  cell_off\n\n"

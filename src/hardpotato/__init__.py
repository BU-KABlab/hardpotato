"""
hardpotato library

A Python library for controlling and interfacing with various potentiostats.

hardpotato provides a unified interface for working with different potentiostat
models, including CHI instruments (CHI601E, CHI760E, CHI1205B, CHI1242B)
and the PalmSens EmStat Pico.

The library allows you to:
- Connect to and configure potentiostats
- Run electrochemical techniques (CV, LSV, CA, OCP, EIS, etc.)
- Load and save experimental data
- Plot results

Quick Start:
-----------
```python
import hardpotato as hp

# Set up the potentiostat
folder = "C:/Users/username/Experiments/data"
hp.potentiostat.Setup('emstatpico', None, folder)

# Run a cyclic voltammetry experiment
cv = hp.potentiostat.CV(
    Eini=-0.5,     # Initial potential (V)
    Ev1=0.5,       # First vertex potential (V)
    Ev2=-0.5,      # Second vertex potential (V)
    Efin=0.0,      # Final potential (V)
    sr=0.1,        # Scan rate (V/s)
    dE=0.001,      # Potential increment (V)
    nSweeps=2,     # Number of sweeps
    sens=1e-6,     # Sensitivity (A/V)
    fileName="CV_test",
    header="CV Test"
)
cv.run()

# Load results from a saved file
data = hp.load_data.CV("CV_test.txt", folder=folder, model="emstatpico")
```

Available modules:
----------------
- potentiostat: Main module for potentiostat control and running techniques
- load_data: Module for loading and parsing experimental data files
- save_data: Module for saving experimental data to files
- chi1205b, chi1242b, chi601e, chi760e: Modules for specific CHI instruments
- emstatpico: Module for the EmStat Pico potentiostat
- pico_instrument, pico_serial, pico_mscript: Low-level modules for EmStat Pico
"""

from . import load_data, potentiostat

__version__ = "1.3.14"
__author__ = "Oliver Rodriguez, Odin Holmes, Gregory Robben"

# modules to import when user does 'from hardpotato import *':
__all__ = ["potentiostat", "load_data"]

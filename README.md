# Hard Potato library

Welcome to the hardpotato GitHub repository. Hard Potato is an open source Python
API to control commercially available potentiostats. It enables researchers to
write Python scripts that can include experimentation, immediate data analysis
using any third-party library and/or the control of other instruments. Hard Potato
facilitates the standardization of electrochemical experiments by keeping a 
record of the experiments and data analysis that can be later run again to ensure 
repeatability. It also facilitates the sharing of electrochemical protocols 
between researchers and groups that own different potentiostats. 

## Supported Potentiostats

Currently, the following potentiostats are included in the library:

* CHI1205B from CH Instruments (chi1205b)
* CHI1242B from CH Instruments (chi1242b)
* CHI601E from CH Instruments (chi601e)
* CHI760E from CH Instruments (chi760e)
* EmStat Pico from PalmSens (emstatpico)
* EmStat4 HR from PalmSens (emstatpico_hr)

## Supported Techniques

All potentiostats:
* Cyclic voltammetry (CV)
* Chronoamperometry (CA)
* Linear sweep voltammetry (LSV)
* Open circuit potential (OCP)

CHI601E and CHI760E only:
* Normal pulse voltammetry (NPV)

EmStat Pico only:
* Electrochemical Impedance Spectroscopy (EIS)

## Installation

From PyPI:
```bash
pip install hardpotato
```

From source:
```bash
pip install git+https://github.com/jrlLAB/hardpotato.git
```

For development:
```bash
git clone https://github.com/jrlLAB/hardpotato.git
cd hardpotato
pip install -e ".[dev]"
```

## Quick Start

```python
import hardpotato as hp

# Potentiostat setup
# Choose the correct model from ['chi760e', 'chi1205b', 'emstatpico']:
model = 'chi760e' 
# Write the path where the chi software is installed (optional for Pico):
path = 'C:/Users/jrl/CHI/chi760e.exe'
# Write the path where data will be saved:
folder = 'C:/Users/jrl/Experiments/data'
# Setup:
hp.potentiostat.Setup(model, path, folder)

# Run CV with default values:
cv = hp.potentiostat.CV()
cv.run()

# Run a LSV with default values:
lsv = hp.potentiostat.LSV()
lsv.run()

# Run a CA with default values:
ca = hp.potentiostat.CA()
ca.run()

# Run an OCP with default values:
ocp = hp.potentiostat.OCP()
ocp.run()
```

## Notes for CH Instruments users

* Since the CHI potentiostat software only works in Windows, any script written with
hardpotato will only work in Windows.
* The CHI translators use macro commands that are only available in the most 
recent versions of the software. Please contact CHI support for help on updating
the potentiostat software and firmware.

## Notes for EmStat Pico users

* Contact PalmSens for instructions on how to update the firmware of the Pico.
* The communication to the Pico is done via the serial port, this means that no
external software is required. Because of this, there is no live plotting, however,
the data and plots are saved when the measurement is finished.
* Scripts written for the pico may also work in other operating systems, provided
the library is installed correctly. So far, hardpotato with the Pico has been 
tested in Windows 10 and Manjaro Linux with kernel 5.15.xx; it has not been tested 
with MacOS although it should work.
* For EmStat4 HR (high range) devices, use `emstatpico_hr` as the model name.

## Requirements

* numpy for data handling
* matplotlib for plotting
* scipy for fitting
* pyserial for serial handling
* [softpotato](https://github.com/oliverrdz/softpotato) for electrochemical equations and simulations

## Acknowledgements

* To CH Instruments for making their software flexible enough that it can be 
started from the Windows command line and for creating the Macros.
* To PalmSens for developing MethodScript and writing code for parsing data. The
code is in the [PalmSens MethodScript GitHub repository](https://github.com/PalmSens/MethodSCRIPT_Examples).
* This development is funded by the Joint Center for Energy Storage Research ([JCESR](https://www.jcesr.org/)).

## Citation

We have published a paper on Analytical Chemistry ([DOI:10.1021/acs.analchem.2c04862](https://doi.org/10.1021/acs.analchem.2c04862)). Please consider citing our work if you use Hard Potato.

## Authors

Hard Potato was developed at the [Beckman Institute](https://beckman.illinois.edu/), University of Illinois at Urbana-Champaign, Feb 2021 to Jan 2023 by:

* Lead: Oliver Rodriguez ([oliverrdz.xyz](https://oliverrdz.xyz), oliver.rdz@softpotato.xyz)
* Support: Michael Pence (mapence2@illinois.edu)
* PI: Joaquin Rodriguez-Lopez (joaquinr@illinois.edu)

# GRAACE-SIM

GRAACE-SIM is a material-agnostic GEANT4 framework for modeling Prompt Gamma
Activation Analysis (PGAA) experiments. It lets you configure materials and
geometries, run simulations, and generate prompt gamma data for experiment
planning and analysis development.

The design is a compiled GEANT4 engine driven by a Python control layer, with
every input and output validated by Pydantic models. You set up a neutron
source, a sample, shielding, and detectors, run a simulation, and get back
gamma-emission data — all without editing or recompiling the GEANT4 code.

```{toctree}
:caption: Overview
:maxdepth: 2

architecture/general
```

```{toctree}
:caption: Simulation engine (C++)
:maxdepth: 1

architecture/simulation/overview
architecture/simulation/configuration
architecture/simulation/messenger
architecture/simulation/geometry
architecture/simulation/actions
architecture/simulation/io
```

```{toctree}
:caption: Python control layer
:maxdepth: 1

architecture/python/models
```

```{toctree}
:caption: Reference
:maxdepth: 2

api/index
```

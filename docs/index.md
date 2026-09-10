# GRAACE-SIM

GRAACE-SIM is a material-agnostic GEANT4 framework for modeling Prompt Gamma Activation Analysis (PGAA) experiments. A Python control layer validates a YAML configuration and writes a GEANT4 macro. The compiled engine reads that macro, transports particles, and writes detector responses as Parquet files.

The two layers communicate through text and files, so changing a material or placement does not require a C++ rebuild. The Python package contains configuration models, YAML loading, macro writing, and process management; the C++ program contains the GEANT4 physics and detector geometry.

```{toctree}
:caption: Start here
:maxdepth: 2

getting-started
```

```{toctree}
:caption: Overview
:maxdepth: 2

architecture/general
architecture/python/models
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
:caption: Reference
:maxdepth: 2

api/index
```



![GRAACE-SIM banner](docs/images/Banner.jpg)

# graace-sim

[![CI](https://github.com/lanl/graace-sim/actions/workflows/validate.yml/badge.svg)](https://github.com/lanl/graace-sim/actions/workflows/validate.yml)
[![Documentation Status](https://readthedocs.org/projects/graace-sim/badge/?version=latest)](https://graace-sim.readthedocs.io/en/latest/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22698352.svg)](https://doi.org/10.5281/zenodo.22698352)

Full documentation: [graace-sim.readthedocs.io](https://graace-sim.readthedocs.io/en/latest/)

GRAACE-SIM is a material-agnostic GEANT4 framework for modeling Prompt Gamma Activation Analysis (PGAA) experiments. It lets you describe a source, sample, shielding, and detectors in YAML, run the compiled simulation engine, and inspect gamma-hit data without editing C++ code.

## Install with Pixi

Install [Pixi](https://pixi.sh/latest/installation/) if it is not already available:

```sh
curl -fsSL https://pixi.sh/install.sh | sh
```

Create a directory for your simulation project and initialize a Pixi workspace:

```sh
mkdir my-simulation
cd my-simulation
pixi init
```

Enable Pixi's package-build preview feature by adding this line under `[workspace]` in the new `pixi.toml`:

```toml
preview = ["pixi-build"]
```

Add the current release. The tag keeps later releases from changing this environment:

```sh
pixi add --git https://github.com/lanl/graace-sim.git --tag v0.2.2 graace-sim
```

Or replace the contents of `pixi.toml` with:

```toml
[workspace]
name = "my-simulation"
channels = ["conda-forge"]
platforms = ["osx-arm64", "linux-64"]
preview = ["pixi-build"]

[dependencies]
graace-sim = { git = "https://github.com/lanl/graace-sim.git", tag = "v0.2.2" }
```

Install the environment:

```sh
pixi install
```

The package supports the `osx-arm64` and `linux-64` Pixi platforms. Pixi builds and installs the GEANT4 engine together with the Python control layer and its runtime dependencies.

## Run a simulation

The public Python interface loads a YAML file and runs the validated configuration:

```python
from graace_sim import load_simulation, run_simulation

simulation = load_simulation("config.yaml")
run_simulation(simulation)
```

The runner finds `graace-sim` on `PATH`, writes a GEANT4 macro, launches the engine, and returns the run directory. A typical run directory contains:

```text
<working_directory>/<run_id>_<sub_run>/
├── <run_id>.mac
├── logs/run.log
└── results/
    ├── geometry.png
    └── <detector_name>/gamma_hits-part-w000-00000.parquet
```

The Parquet files contain one row for each detector response, with `energy` in keV and `time` in ns. The automatic geometry picture is written when an offscreen graphics driver is available; it is skipped for an interactive viewer or a build without that driver.

See the [getting started guide](https://graace-sim.readthedocs.io/en/latest/getting-started.html) for a complete example and output-reading instructions.

## Run the repository examples

The YAML files and helper scripts under `examples/` are included in the source repository, but are not installed by the Pixi package. To run them, clone the repository and work from its root:

```sh
git clone https://github.com/lanl/graace-sim.git
cd graace-sim
pixi install
pixi run --locked python examples/scripts/run_from_yaml.py examples/yaml_files/ni58_enriched.yaml
```

The repository workspace also provides these useful tasks:

```sh
pixi run --locked test
pixi run --locked build-sim
```

For an installed package in a separate project, use your own YAML configuration with the Python interface above.
## Copyright

© 2026. Triad National Security, LLC. All rights reserved.

This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL), which is operated by Triad National Security, LLC for the U.S. Department of Energy/National Nuclear Security Administration. All rights in the program are reserved by Triad National Security, LLC, and the U.S. Department of Energy/National Nuclear Security Administration. The Government is granted for itself and others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so.

O# (O5117)

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license text is in the [LICENSE](LICENSE) file.

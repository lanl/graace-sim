

![GRAACE-SIM banner](docs/images/Banner.jpg)

# graace-sim

[![Documentation Status](https://readthedocs.org/projects/graace-sim/badge/?version=latest)](https://graace-sim.readthedocs.io/en/latest/)

Full documentation: [graace-sim.readthedocs.io](https://graace-sim.readthedocs.io/en/latest/)

GRAACE-SIM is a material-agnostic GEANT4 framework for modeling Prompt Gamma Activation Analysis (PGAA) experiments, enabling users to configure materials and geometries, run simulations, and generate prompt gamma data for experiment planning and analysis development.

## Install with Pixi

Install Pixi if it is not already available:

```sh
curl -fsSL https://pixi.sh/install.sh | sh
```

Create a directory for your simulation project and initialize a Pixi workspace:

```sh
mkdir my-simulation
cd my-simulation
pixi init
```

Before adding GRAACE-SIM, enable Pixi's package-build preview feature in the
new `pixi.toml` file by adding this line under `[workspace]`:

```toml
preview = ["pixi-build"]
```

Add the GRAACE-SIM release you want. The tag pins the package version so later
releases do not change an existing environment:

```sh
pixi add --git https://github.com/lanl/graace-sim.git --tag v0.2.0 graace-sim
```

Alternatively, replace the contents of `pixi.toml` with:

```toml
[workspace]
name = "my-simulation"
channels = ["conda-forge"]
platforms = ["osx-arm64", "linux-64"]
preview = ["pixi-build"]

[dependencies]
graace-sim = { git = "https://github.com/lanl/graace-sim.git", tag = "v0.2.0" }
```

Install the environment:

```sh
pixi install
```

Pixi builds the GEANT4 engine and installs it together with the Python package
and its runtime dependencies. The package currently supports `osx-arm64` and
`linux-64` Pixi platforms.

The public Python interface is:

```python
from graace_sim import load_simulation, run_simulation

graace_record = load_simulation("config.yaml")
run_simulation(graace_record)
```

## Run a simulation

Create a YAML configuration file in your project, then load and run it with the
public Python interface:

```python
from graace_sim import load_simulation, run_simulation

graace_record = load_simulation("config.yaml")
run_simulation(graace_record)
```

The run writes the macro, engine log, geometry image, and detector Parquet files
under the `working_directory` and `run_id` from your configuration.

## Repository examples

The YAML files and helper scripts under `examples/` are included in the source
repository, but are not installed by the Pixi package. To run them, clone the
repository and work from its root:

```sh
git clone https://github.com/lanl/graace-sim.git
cd graace-sim
pixi install
pixi run python examples/scripts/run_from_yaml.py examples/yaml_files/ni58_enriched.yaml
```

For an installed package in a separate project, use your own YAML configuration
with the Python interface shown above.
## Copyright

© 2026. Triad National Security, LLC. All rights reserved.

This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL), which is operated by Triad National Security, LLC for the U.S. Department of Energy/National Nuclear Security Administration. All rights in the program are reserved by Triad National Security, LLC, and the U.S. Department of Energy/National Nuclear Security Administration. The Government is granted for itself and others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so.

O# (O5117)

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license text is in the [LICENSE](LICENSE) file.

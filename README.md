

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

## Running Examples

Once the GRAACE-SIM environment is set up and the simulation is built, you can run the following examples:
1. Run via a yaml config file from the root directory:

   ```
   pixi run python examples/scripts/run_from_yaml.py examples/yaml_files/ni58_enriched.yaml
   ```

   This writes the macro, launches the simulation, shows the progress, and saves outputs
   under `data/<run_id>_<sub_run>/`:

   ```
   data/ni58_enriched_000/
     ni58_enriched.mac              the exact macro that ran
     results/<detector>/*.parquet   the gamma hits, one directory per detector
     logs/run.log                   the engine's streamed output
   ```

2. Run the simulation to verify geometries and run interactively:

   ```
   pixi run graace-sim
   ```

   This launches the simulation in interactive mode, allowing you to verify geometries and interact with the simulation environment.

   In the session terminal you can run the following commands to start the simulation: 

   ```
   /run/beamOn 100
   ```

   This will run the simulation for 100 neutron beam events. Don't do anything over 1000 otherwise it becomes visually cluttered in the GEANT4 interactive viewer.

## Copyright

© 2026. Triad National Security, LLC. All rights reserved.

This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL), which is operated by Triad National Security, LLC for the U.S. Department of Energy/National Nuclear Security Administration. All rights in the program are reserved by Triad National Security, LLC, and the U.S. Department of Energy/National Nuclear Security Administration. The Government is granted for itself and others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so.

O# (O5117)

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license text is in the [LICENSE](LICENSE) file.

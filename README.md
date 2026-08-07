# graace-sim

GRAACE-SIM is a material-agnostic GEANT4 framework for modeling Prompt Gamma Activation Analysis (PGAA) experiments, enabling users to configure materials and geometries, run simulations, and generate prompt gamma data for experiment planning and analysis development.

## Getting Started

In order to run the simulation you need to have the pixi environment set up. Pixi can be install via:

```
curl -fsSL https://pixi.sh/install.sh | sh
```

Once pixi is installed, you can set up the GRAACE-SIM environment and build the geant4 simulation by running:

```
pixi run build-sim
```
This installs the `graace-sim` binary into the pixi environment's `bin`, so `which graace-sim` finds it.

## Running Examples

Once the GRAACE-SIM environment is set up and the simulation is built, you can run the followingexamples:
1. Run via a yaml config file from the root directory:

   ```
   pixi run python examples/run_from_yaml.py examples/yaml_files/ni58_enriched.yaml
   ```

   This writes the macro, launches the simulation, shows the progress, and saves outputs
   under `data/<run_id>_<sub_run>/`:

   ```
   data/ni58_enriched_000/
     ni58_enriched.mac              the exact macro that ran
     results/<detector>/*.parquet   the gamma hits, one directory per detector
     logs/run.log                   the engine's streamed output
   ```

   Re-running the same config is safe: it re-writes the macro and re-runs.

2. Run the simulation to verfify geometries and run interactively:

   ```
   pixi run graace-sim
   ```

   This launches the simulation in interactive mode, allowing you to verify geometries and interact with the simulation environment.

   In the session terminal you can run the following commands to start the simulation: 

   ```
   /run/beamOn 100
   ```

   This will run the simulation for 100 neutron beam events.

## Copyright

O# (O5117)

© 2026. Triad National Security, LLC. All rights reserved.

This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL), which is operated by Triad National Security, LLC for the U.S. Department of Energy/National Nuclear Security Administration. All rights in the program are reserved by Triad National Security, LLC, and the U.S. Department of Energy/National Nuclear Security Administration. The Government is granted for itself and others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so.

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license text is in the [LICENSE](LICENSE) file.

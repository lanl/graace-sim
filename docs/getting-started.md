# Getting started

GRAACE-SIM supports two ways to get started:

- **Install a released package in your own Pixi project** when you are starting a new simulation project and do not need the source tree.
- **Clone the repository** when you want the included examples, source code, tests, or build tasks.

Both paths install the Python package, the `graace-sim` simulation engine, and the GEANT4 runtime. They support `osx-arm64` and `linux-64` systems.

If Pixi is not installed, follow the [Pixi installation instructions](https://pixi.sh/latest/installation/) first.

## Use a released package in a new Pixi project

This path keeps your simulation configuration and results separate from the GRAACE-SIM source code. The instructions below use the `v0.2.2` release. Replace that tag with a later release when one is available.

Create a directory for your project and initialize a Pixi workspace:

```sh
mkdir my-simulation
cd my-simulation
pixi init
```

Add the Pixi build preview setting under `[workspace]` in the new `pixi.toml`:

```toml
preview = ["pixi-build"]
```

Then add the pinned GRAACE-SIM release:

```sh
pixi add --git https://github.com/lanl/graace-sim.git --tag v0.2.2 graace-sim
```

The command adds the dependency to `pixi.toml`. If you prefer to edit the file yourself, the relevant parts look like this:

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

The package includes the `graace_sim` Python interface, the `graace-sim` executable, and their runtime dependencies. The repository's `examples/` directory is not part of the installed package, so create or copy a YAML configuration into your own project.

### Create and run a configuration

A configuration needs a source, at least one detector, run settings, and run metadata. For a small first run, create `config.yaml`:

```yaml
source:
  particle: neutron
  position:
    shape: point
    center_mm: {x_mm: 0, y_mm: 0, z_mm: -50}
  energy:
    type: mono
    mono_mev: 14.1

detectors:
  - name: hpge
    type: HPGe
    position_mm: {x_mm: 0, y_mm: 80, z_mm: 0}
    dimension_mm: {x_mm: 60, y_mm: 60, z_mm: 50}

run:
  neutrons: 1000

metadata:
  author: my-simulation
  date: "2026-09-11"
  description: First GRAACE-SIM run.
```

Create `run.py` next to it:

```python
from graace_sim import load_simulation, run_simulation

simulation = load_simulation("config.yaml")
run_simulation(simulation)
```

Run it from the Pixi environment:

```sh
G4VIS_DEFAULT_DRIVER=TSG_OFFSCREEN pixi run --locked python run.py
```

The offscreen setting is useful on a computer without an interactive display. You can omit it when your graphics setup provides an appropriate GEANT4 driver.

## Clone the repository and use its Pixi workspace

Choose this path for the checked-in examples, source code, tests, or package build tasks. Clone the repository and install the environment defined by its `pixi.toml`:

```sh
git clone https://github.com/lanl/graace-sim.git
cd graace-sim
pixi install
```

For a reproducible released checkout, clone the release tag instead:

```sh
git clone --branch v0.2.2 https://github.com/lanl/graace-sim.git
cd graace-sim
pixi install
```

The repository workspace uses `graace-sim = { path = "." }`. Pixi builds the local package and installs it into the workspace environment. It also makes the `examples/` directory and repository tasks available.

Run the checked-in example from the repository root:

```sh
pixi run --locked python examples/scripts/run_from_yaml.py examples/yaml_files/example.yaml
```

On a headless machine, use the offscreen graphics driver:

```sh
G4VIS_DEFAULT_DRIVER=TSG_OFFSCREEN \
pixi run --locked python examples/scripts/run_from_yaml.py examples/yaml_files/example.yaml
```

Other configurations are available in `examples/yaml_files/`. The helper script must be run from the repository root because its paths refer to the `examples/` directory.

The repository also provides tasks for development:

```sh
pixi run --locked test
pixi run --locked build-sim
```

`build-sim` is normally not needed after `pixi install`; use it if you need to rebuild the local package after changing the source.

## Understand a run

The checked-in example writes its files under `data/example_000/`:

```text
data/example_000/
├── example.mac
├── logs/run.log
└── results/
    ├── geometry.png
    └── hpge/
        └── gamma_hits-part-w000-00000.parquet
```

The exact number of Parquet part files depends on the worker threads and the detector responses. Each detector has its own directory. The files contain:

| Column | Unit | Meaning |
| --- | --- | --- |
| `energy` | keV | Total energy deposited in the detector during the event |
| `time` | ns | Time of the earliest energy deposit in the event |

Each row represents one detector response for one event. Read all parts for one detector with PyArrow:

```python
from pathlib import Path
import pyarrow.dataset as ds

parts = Path("data/example_000/results/hpge")
hits = ds.dataset(parts, format="parquet").to_table()
print(hits.schema)
print(hits.to_pandas().head())
```

The `.mac` file contains the GEANT4 commands generated from the YAML configuration. The log at `logs/run.log` contains the engine output and is the first place to look after a failed run. `geometry.png` is optional: it is written when an offscreen graphics driver is available and may be absent when graphics support is unavailable or an interactive viewer is already active.

## Write your own configuration

Start with the example YAML or the minimal configuration above. The required top-level sections are:

- `source`: particle, position, energy, and optional timing;
- `detectors`: one or more named detector descriptions;
- `run`: neutron count and optional random seed;
- `metadata`: author, date, and description.

`sample` is optional. `shielding`, `environment`, and `runner` have defaults. Positions and sizes are in millimeters, source energy is in MeV, density is in g/cm³, detector energy resolution is in keV, and source timing is in ns. See the [Python model guide](architecture/python/models.md) for the available fields and defaults.

The Python models reject unknown keys and invalid values before the engine starts. Keep the YAML file with the generated macro when you need to reproduce or compare a run; the runner does not copy the validated configuration into the output directory.

## Common problems

| Message or symptom | What to check |
| --- | --- |
| `graace-sim is not on PATH` | Run the command inside the Pixi environment. In a repository checkout, `pixi install` normally builds the local package; use `pixi run --locked build-sim` to rebuild it after source changes. |
| Pixi cannot build the Git dependency | Confirm that `preview = ["pixi-build"]` is under `[workspace]`, then run `pixi install` again. |
| Pydantic validation error | Check the field named in the error. Names use the YAML path, such as `source.energy.mono_mev`. |
| No geometry picture | Set `G4VIS_DEFAULT_DRIVER=TSG_OFFSCREEN`, or inspect the log. A run can finish without a geometry picture when graphics support is unavailable. |
| Missing Parquet output | Inspect `logs/run.log` and confirm that each detector has a unique name. The default output check requires at least one Parquet file for every detector. |
| Spectrum source falls back to mono energy | Check that `source.energy.spectrum_file` is readable from the process working directory and contains `energy_mev intensity` pairs, one per line. |

## Next steps

- Read the [Python model guide](architecture/python/models.md) to learn the YAML fields.
- Read the [output guide](architecture/simulation/io.md) for Parquet files and worker part files.
- In a repository checkout, browse the other files under `examples/yaml_files/` for sample, shielding, timing, and multiple-detector setups.

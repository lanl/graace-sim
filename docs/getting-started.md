# Getting started

This guide runs the checked-in example from a source checkout. It is the easiest way to confirm that the engine, Python package, and GEANT4 data are installed correctly.

## Install the repository environment

```sh
git clone https://github.com/lanl/graace-sim.git
cd graace-sim
pixi install
```

The repository workspace supports `osx-arm64` and `linux-64`. The package build supplies the `graace-sim` executable and installs the Python package in the same environment.

## Run an example

Run the small iron-sample example:

```sh
pixi run --locked python examples/scripts/run_from_yaml.py examples/yaml_files/example.yaml
```

The YAML file is loaded and validated before the runner writes a macro and starts the engine. To choose another setup, pass one of the files under `examples/yaml_files/` instead.

For headless machines, select an offscreen graphics driver. The engine can still complete a run without a geometry picture if no offscreen driver is available, but `TSG_OFFSCREEN` is the setting used by CI:

```sh
G4VIS_DEFAULT_DRIVER=TSG_OFFSCREEN \
pixi run --locked python examples/scripts/run_from_yaml.py examples/yaml_files/example.yaml
```

## Find the results

The example defaults to `data/example_000/`:

```text
data/example_000/
├── example.mac
├── logs/run.log
└── results/
    ├── geometry.png
    └── hpge/
        └── gamma_hits-part-w000-00000.parquet
```

The exact part-file count depends on the number of worker threads and the number of detector hits. Each detector has its own directory. A file contains two columns:

| Column | Unit | Meaning |
| --- | --- | --- |
| `energy` | keV | Total energy deposited in the detector during the event |
| `time` | ns | Time of the earliest energy deposit in the event |

A row is one detector response for one event. The detector name is supplied by the directory rather than repeated as a column.

Read all parts for one detector with PyArrow:

```python
from pathlib import Path
import pyarrow.dataset as ds

parts = Path("data/example_000/results/hpge")
hits = ds.dataset(parts, format="parquet").to_table()
print(hits.schema)
print(hits.to_pandas().head())
```

The generated `.mac` file is useful when checking exactly which GEANT4 commands were sent to the engine. The log contains the engine output and is the first place to look after a failed run.

## Write your own configuration

Start with `examples/yaml_files/example.yaml`. The required top-level sections are:

- `source`: particle, position, energy, and optional timing;
- `detectors`: one or more named detector descriptions;
- `run`: neutron count and optional random seed;
- `metadata`: author, date, and description.

`sample` is optional. `shielding`, `environment`, and `runner` have defaults. Positions and sizes are in millimeters, source energy is in MeV, density is in g/cm³, detector energy resolution is in keV, and source timing is in ns.

The Python models reject unknown keys and invalid values before the engine starts. Keep the original YAML with the generated macro when you need to reproduce or compare a run; the current runner does not write a separate copy of the validated configuration into the output directory.

## Common problems

| Message or symptom | What to check |
| --- | --- |
| `graace-sim is not on PATH` | From a repository checkout, run `pixi run --locked build-sim`; from an installed package, run inside the Pixi environment that contains GRAACE-SIM. |
| Pydantic validation error | Check the field named in the error. Names use the YAML path, such as `source.energy.mono_mev`. |
| No geometry picture | Set `G4VIS_DEFAULT_DRIVER=TSG_OFFSCREEN`, or inspect the log; the simulation can continue without a picture when graphics support is unavailable. |
| Missing Parquet output | Inspect `logs/run.log`. If output verification is enabled, the runner requires at least one Parquet file for every detector. |
| Spectrum source falls back to mono energy | Check that `source.energy.spectrum_file` is readable from the process working directory and contains `energy_mev intensity` pairs, one per line. |

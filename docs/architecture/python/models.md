# Python configuration models

The Pydantic models under `src/graace_sim/models/` describe one experiment and
validate it before the engine starts. Unknown keys are rejected and assignments
are re-validated.

## Top-level configuration

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
  neutrons: 10000

metadata:
  author: researcher
  date: "2026-09-10"
  description: Example PGAA run
```

Required top-level fields are `source`, `detectors`, `run`, and `metadata`.
`sample` is optional. `shielding`, `environment`, and `runner` have defaults.
Python and YAML fields use `snake_case`; GEANT4 command names use the spelling
registered by the C++ messenger, such as `/source/energyType`.

## Validation rules

All models inherit from `StrictModel`:

```python
class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
```

Positions are `Vec3Mm` values and may be negative. `Size3Mm` values must be
positive. Numeric names include their units: `position_mm`, `density_g_cm3`,
`mono_mev`, `energy_resolution_kev`, and `pulse_width_ns`.

## Source

`Source` contains `position`, `energy`, and optional `timing` fields.

- `position.shape` is `point`, `disk`, or `beam`. A disk uses `radius_mm` as a
  hard disk radius. A beam passes the value to GEANT4 as the radial Gaussian sigma.
- `energy.type` is `mono` or `spectrum`. A mono source requires `mono_mev`.
  A spectrum source requires a readable text file whose non-comment rows contain
  `energy_mev intensity` pairs, one pair per line.
- `timing.mode` is `continuous`, `single`, or `periodic`. Single and periodic
  modes require `pulse_width_ns`; periodic mode also requires `pulse_period_ns`.

Example spectrum source:

```yaml
source:
  particle: neutron
  position:
    shape: point
    center_mm: {x_mm: 0, y_mm: 0, z_mm: -50}
  energy:
    type: spectrum
    spectrum_file: data/source-spectrum.txt
  timing:
    mode: periodic
    pulse_width_ns: 10
    pulse_period_ns: 1000
```

The spectrum path is read by the engine from the process working directory. If
the file cannot be opened, the engine reports the problem and falls back to its
mono-energy setting.

## Sample

A sample has a material composition, density, shape, dimensions, and position.
`shape` is `cube`, `sphere`, or `cylinder`; a cylinder requires `height_mm`.
`size_mm` is the cube side or sphere/cylinder radius. Element mass fractions must
sum to 1.0. An element may include isotope entries whose atom fractions sum to
1.0; an element without entries uses natural isotopic abundances.

## Detectors

A detector requires a unique `name`, `type`, `position_mm`, and `dimension_mm`.
The engine currently constructs every detector as an HPGe cylinder. The macro
writer maps `dimension_mm.x_mm / 2` to the cylinder radius and `dimension_mm.z_mm`
to its height; `dimension_mm.y_mm` is validated but is not used in the engine
geometry. `energy_resolution_kev` is accepted by the Python model but is not yet
sent to GEANT4 or applied to the recorded energy.

## Shielding

Each shielding entry supplies a GEANT4 material name, positive
`thickness_mm`, and `position_mm`. The engine uses a fixed 200 mm square footprint
for each slab; only material, thickness, and position are configurable.

## Run, runner, and environment

`run.neutrons` must be positive. `run.seed` defaults to zero. A serial run can be
reproduced with the same seed; multithreaded runs are statistically reproducible,
but event order can differ.

`runner` controls launch behavior:

```yaml
runner:
  binary: graace-sim
  show_progress: true
  verify_output: true
  cpu_percent: 80
```

`cpu_percent` determines the number of GEANT4 worker threads as a percentage of
logical CPU cores, with at least one thread.

`environment` controls the output layout:

```yaml
environment:
  working_directory: data
  run_id: example
  sub_run: 0
```

This creates `data/example_000/` with the macro, log, and results directories.

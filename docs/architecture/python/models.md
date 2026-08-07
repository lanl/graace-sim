# Pydantic Models

The Pydantic models are the configuration schema for GRAACE-SIM. They describe
one experiment — the neutron source, the sample, the detectors, the shielding,
and the run settings — and validate it before anything runs. The validated
top-level model is also the run record: it is written out with the results so a
run always carries the exact settings that produced it.

All models live in `src/models/`.

## The strict base

Every model inherits from one base class, `StrictModel`, which sets the
validation rules for the whole schema:

```python
from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Base model with strict validation defaults."""

    model_config = ConfigDict(
        extra="forbid",            # reject unknown fields
        validate_assignment=True,  # re-validate when a field is changed
    )
```

- `extra="forbid"` — a typo in a config key is an error, not a silently ignored
  field.
- `validate_assignment=True` — changing a field after construction re-runs
  validation, so a model can never be edited into an invalid state.

Every field is `snake_case`, in both the config and the output — see
[Naming](#naming-always-snake_case).

## Small reusable vectors

Positions and sizes are their own small models, reused everywhere by
composition. Sizes must be positive; positions may be negative.

```python
class Vec3Mm(StrictModel):
    """A 3D position in millimeters. Any sign allowed."""
    x_mm: float
    y_mm: float
    z_mm: float


class Size3Mm(StrictModel):
    """A 3D size in millimeters. Every side must be positive."""
    x_mm: float = Field(gt=0)
    y_mm: float = Field(gt=0)
    z_mm: float = Field(gt=0)
```

## The top-level model

`Simulation` is a flat composition of the parts of an experiment. Required parts
have no default; optional parts are `X | None = None`. `source`, `detectors`,
`run`, and `metadata` are required. `sample` is optional (a setup may have no
sample), and `shielding` defaults to an empty list. `environment` and `runner`
both default, so an existing config with neither block stays valid.

```python
class Simulation(StrictModel):
    """Top-level GRAACE-SIM configuration and run record."""

    source: Source
    sample: Sample | None = None
    detectors: list[Detector]
    shielding: list[Shielding] = []
    run: RunSettings
    metadata: Metadata
    environment: WorkingEnvironment = Field(default_factory=WorkingEnvironment)
    runner: SimRunner = Field(default_factory=SimRunner)
```

Each part is defined in its own file under `src/models/` and imported here.

## The parts

### Source (`source.py`)

The neutron source, described through GEANT4's General Particle Source. `Source`
is a composition of four independent parts, so each can be varied without
touching the others:

```python
class Source(StrictModel):
    particle: str = Field(default="neutron", min_length=1)
    position: SourcePosition
    energy: SourceEnergy
    timing: SourceTiming = Field(default_factory=SourceTiming)
```

- **`position`** — where and how the neutrons start (a point, a disk, a beam).
- **`energy`** — a single energy, or a full spectrum from an external file.
- **`timing`** — continuous, a single pulse, or periodic pulses.

The design goal is flexibility: a simple DT generator is a one-energy continuous
source; a beamline concept is a spectrum-from-file pulsed source. Both are the
same `Source` model with different parts filled in.

#### Position

Where the neutrons originate and the emission shape, following the General
Particle Source geometry. A `radius_mm` is required only for shapes that need one
(a disk or sphere), so it is optional at the schema level and enforced by an
after-validator.

```python
class SourcePosition(StrictModel):
    shape: Literal["point", "disk", "beam"] = "point"
    center_mm: Vec3Mm
    radius_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_radius(self) -> "SourcePosition":
        if self.shape in {"disk", "beam"} and self.radius_mm is None:
            raise ValueError("`source.position.radius_mm` is required for shape 'disk' or 'beam'.")
        return self
```

#### Energy

The neutron energy, either a single value or a full spectrum read from an
external list file. This is the "which fields are required depends on a mode"
pattern: the value-bearing fields are optional, and an after-validator enforces
the one the chosen `type` needs.

- **`mono`** — a single energy in MeV (a DT generator at 14.1 MeV, a DD generator
  at 2.45 MeV).
- **`spectrum`** — a path to a plain text list file of `energy_mev intensity`
  pairs (one per line), for a distributed source such as a Cf-252 spectrum or a
  measured beam spectrum. The file is referenced here and read at run time, not
  copied into the config.

```python
class SourceEnergy(StrictModel):
    type: Literal["mono", "spectrum"] = "mono"
    mono_mev: float | None = Field(default=None, gt=0)
    spectrum_file: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def check_energy(self) -> "SourceEnergy":
        if self.type == "mono" and self.mono_mev is None:
            raise ValueError("`source.energy.mono_mev` is required when type is 'mono'.")
        if self.type == "spectrum" and self.spectrum_file is None:
            raise ValueError("`source.energy.spectrum_file` is required when type is 'spectrum'.")
        return self
```

#### Timing

The time structure of the source — nothing more. There are three modes:

- **`continuous`** — the source emits steadily. No extra fields.
- **`single`** — one pulse of a given width. Requires `pulse_width_ns`.
- **`periodic`** — pulses of a given width, repeating every `pulse_period_ns`.
  Requires both.

Which fields are required depends on the `mode`, so they are optional at the
schema level and an after-validator enforces the ones each mode needs.

```python
class SourceTiming(StrictModel):
    mode: Literal["continuous", "single", "periodic"] = "continuous"
    pulse_width_ns: float | None = Field(default=None, gt=0)
    pulse_period_ns: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_timing(self) -> "SourceTiming":
        if self.mode in {"single", "periodic"} and self.pulse_width_ns is None:
            raise ValueError("`source.timing.pulse_width_ns` is required for mode 'single' or 'periodic'.")
        if self.mode == "periodic" and self.pulse_period_ns is None:
            raise ValueError("`source.timing.pulse_period_ns` is required for mode 'periodic'.")
        return self
```

Two patterns recur in `Source` and are worth naming, because the rest of the
schema reuses them:

- **Single value or external file.** The energy is either an inline value or a
  `*_file` path to an external list file. The config records the file path only;
  the file is read at run time. This keeps large tables out of the config while
  the config still fully describes the run.
- **Conditional-required fields.** The fields a `mode`/`type` needs are optional
  at the schema level and enforced by a `mode="after"` validator. See
  [Conditional-required fields](#conditional-required-fields).

### Sample (`sample.py`)

The material being assayed: its composition, density, shape, dimensions, and
position. Composition is given as element mass fractions that must sum to 1.0.
Element symbols are checked against the periodic table.

Each element may optionally carry an isotope breakdown. Without one, the engine
uses the element's natural isotopic abundances (the common case). With one, the
element is built from the listed isotopes, each given as an **atom fraction**
(fraction by number of atoms — what Geant4 and natural abundances use). The atom
fractions must sum to 1.0 and mass numbers must be unique. This is opt-in: an
element with no `isotopes` key behaves exactly as before.

```python
CHEMICAL_ELEMENT_SYMBOLS = frozenset({"H", "He", "Li", ...})  # full periodic table
COMPOSITION_TOLERANCE = 1.0e-6


class SampleIsotope(StrictModel):
    mass_number: int = Field(gt=0)
    atom_fraction: float = Field(gt=0.0, le=1.0)


class SampleElement(StrictModel):
    symbol: str
    mass_fraction: float = Field(gt=0.0, le=1.0)
    isotopes: list[SampleIsotope] | None = Field(default=None, min_length=1)

    @field_validator("symbol")
    @classmethod
    def known_element(cls, symbol: str) -> str:
        if symbol not in CHEMICAL_ELEMENT_SYMBOLS:
            raise ValueError(f"unknown chemical element symbol: {symbol!r}")
        return symbol

    @model_validator(mode="after")
    def check_isotopes(self) -> "SampleElement":
        if self.isotopes is None:
            return self
        mass_numbers = [isotope.mass_number for isotope in self.isotopes]
        if len(mass_numbers) != len(set(mass_numbers)):
            raise ValueError(f"duplicate isotope mass number in element {self.symbol!r}")
        total = sum(isotope.atom_fraction for isotope in self.isotopes)
        if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=COMPOSITION_TOLERANCE):
            raise ValueError(
                f"isotope atom fractions for element {self.symbol!r} must sum to 1.0"
            )
        return self


class SampleComposition(StrictModel):
    density_g_cm3: float = Field(gt=0)
    elements: list[SampleElement] = Field(min_length=1)

    @model_validator(mode="after")
    def check_fractions(self) -> "SampleComposition":
        symbols = [e.symbol for e in self.elements]
        if len(symbols) != len(set(symbols)):
            raise ValueError("duplicate element symbol")
        total = sum(e.mass_fraction for e in self.elements)
        if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=COMPOSITION_TOLERANCE):
            raise ValueError("element mass fractions must sum to 1.0")
        return self
```

Fraction sums are checked with `math.isclose(total, 1.0, abs_tol=...)` against a
module-level tolerance constant — never `==`, which would fail on rounding.

### Detector (`detector.py`)

One gamma detector: its type (for example HPGe), dimensions, position relative to
the sample, and energy resolution. A `Simulation` holds a `list[Detector]`, so a
setup can include more than one.

```python
class Detector(StrictModel):
    type: str = Field(min_length=1)
    position_mm: Vec3Mm
    dimension_mm: Size3Mm
    energy_resolution_kev: float | None = Field(default=None, gt=0)
```

### Shielding (`shielding.py`)

Optional shielding blocks: material, thickness, and placement. `Simulation`
defaults `shielding` to an empty list, so a setup with no shielding is valid.

```python
class Shielding(StrictModel):
    material: str = Field(min_length=1)
    thickness_mm: float = Field(gt=0)
    position_mm: Vec3Mm
```

### RunSettings (`run.py`)

How the engine runs: how many neutrons to simulate, the random seed, and physics
options.

```python
class RunSettings(StrictModel):
    neutrons: int = Field(gt=0)
    seed: int = Field(default=0, ge=0)
```

`seed` reaches the engine as GEANT4's built-in `/random/setSeeds` command, set
right after `/run/initialize`. A serial run (`cpu_percent` giving one thread) is
then fully reproducible: the same seed gives byte-identical output. A
multithreaded run is not reproducible even at a fixed seed — GEANT4's neutron
physics samples in a thread-order-dependent way — but runs still agree within
counting statistics. Run serial when you need an exactly reproducible run.

### SimRunner (`runner.py`)

How to *launch* the engine, kept separate from `RunSettings` (`run`), which is
the *physics* of the run. `SimRunner` carries the binary name and the launch
options the runner acts on: whether to draw a progress bar, whether to verify
each detector produced results, and how much of the machine's CPU a run may use.
The binary defaults to `graace-sim` and is resolved on PATH, so a config never
records where the build lives.

```python
class SimRunner(StrictModel):
    binary: str = Field(default="graace-sim", min_length=1)
    show_progress: bool = Field(default=True)
    verify_output: bool = Field(default=True)
    cpu_percent: int = Field(default=80, ge=1, le=100)
```

`cpu_percent` caps how much of the machine one run takes. The engine runs
multithreaded, and the macro writer turns this percentage into the engine's
thread count — `max(1, floor(cores * cpu_percent / 100))` over the machine's
logical cores — emitted as `/run/numberOfThreads` before `/run/initialize`. The
default of 80 leaves the machine responsive; set it to 100 to use every core.
That single setting is the whole control: there is no separate override, and the
engine never exceeds it.

`run:` (physics) and `runner:` (launch) read closely; keeping them apart means a
config can change the neutron count without touching how the engine is invoked,
and neither block is required — both default.

### Metadata (`metadata.py`)

Bookkeeping for a run: who made it, when, and what it is. Where the run's files
live is a separate concern, handled by `WorkingEnvironment` below.

```python
class Metadata(StrictModel):
    author: str = Field(min_length=1)
    date: str = Field(min_length=1)
    description: str = Field(min_length=1)
```

### WorkingEnvironment (`environment.py`)

The run's identity and where its files live. These are computed paths only —
nothing here touches the filesystem; creating the directories is the runner's
job. The run directory is `<run_id>_<run_sub_number>` (for example `example_000`) under the
working directory, with fixed `logs/` and `results/` sub-directories and the
exact macro that ran alongside them.

```python
class WorkingEnvironment(StrictModel):
    working_directory: Path = Field(default=Path("data"))
    run_id: str = Field(default="example", min_length=1)
    sub_run: int = Field(default=0, ge=0, le=9999)

    @property
    def run_directory(self) -> Path:
        return self.working_directory / f"{self.run_id}_{self.sub_run:03d}"

    @property
    def log_directory(self) -> Path:
        return self.run_directory / "logs"

    @property
    def results_directory(self) -> Path:
        return self.run_directory / "results"

    @property
    def macro_file(self) -> Path:
        return self.run_directory / f"{self.run_id}.mac"
```

The layout is:

```
<working_directory>/<run_id>_<run_sub_number>/            the run directory
<working_directory>/<run_id>_<run_sub_number>/logs/       summary and log files
<working_directory>/<run_id>_<run_sub_number>/results/    gamma hit Parquet files
<working_directory>/<run_id>_<run_sub_number>/<run_id>.mac the exact macro that ran
```

## Conventions

These are the patterns to follow when adding or changing models.

### Naming: always snake_case

Every field is `snake_case`, and that is the only spelling. Configs are written
in `snake_case` and serialized back in `snake_case`. There are no aliases and no
`camelCase` — one name per field, everywhere, so a key looks the same in the
model, the config file, and the output.

> **NO ALIASING.** Do not add Pydantic aliases (`alias`, `validation_alias`,
> `serialization_alias`, `AliasChoices`) to any field. One `snake_case` name per
> field, no exceptions.

### Units in the name

Numeric fields carry their unit as a suffix — `position_mm`, `density_g_cm3`,
`energy_resolution_kev`, `mono_mev`. The unit is then unambiguous at every use
site and in the output.

### Optional fields and defaults

- A whole part that may be absent: `X | None = None` (for example
  `energy_resolution_kev`).
- A scalar with a sensible default: `Field(default=..., ...)`.
- A nested model with a default: `Field(default_factory=SubModel)`.
- Bounds go inline on the field: `gt`, `ge`, `le`, `min_length`.

### Validators

- `@field_validator` (classmethod) for a single-field check — for example, a
  symbol being in the periodic table, or a string not being blank.
- `@model_validator(mode="after")`, returning `self`, for cross-field rules —
  for example, mass fractions summing to 1.0, or a field being required only for
  a certain `type`. This is the default kind.
- `@model_validator(mode="before")` (classmethod) only to normalize the shape of
  the input before validation (for example, accepting a `[x, y, z]` list where a
  vector model is expected).

Error messages name the field with its dotted config path in backticks — for
example, `` `source.energy.mono_mev` is required when type is 'mono'. `` — so a
user can find the offending key in their config.

### Conditional-required fields

When which fields are required depends on a mode or type, declare them all as
`X | None = None` and enforce the requirement in a `mode="after"` validator keyed
off the mode. See `SourceEnergy` above.

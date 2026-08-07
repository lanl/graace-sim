# Command Interface (Messenger)

The command interface defines the GEANT4 UI commands the engine understands —
the `/source/*`, `/sample/*`, `/detector/*`, `/shielding/*`, and `/output/*`
groups listed in [configuration.md](configuration.md). It is the piece that
turns a line of a macro into a stored value the rest of the engine reads.

It is built on GEANT4's `G4UImessenger`.

## The commands

Every command takes its whole argument as one string, parsed in `SetNewValue`.
Vectors are `x y z` in mm. The current commands:

| Command | Argument | Config field |
| --- | --- | --- |
| `/source/particle` | name | `source_particle` |
| `/source/position` | `x y z` (mm) | `source_position` |
| `/source/shape` | `point \| disk \| beam` | `source_shape` |
| `/source/radius` | mm (disk/beam) | `source_radius` |
| `/source/energyType` | `mono \| spectrum` | `source_energy_type` |
| `/source/energy` | MeV (mono) | `source_energy` |
| `/source/spectrumFile` | path to an `energy_mev intensity` list | `source_spectrum_file` |
| `/source/timing` | `continuous \| single \| periodic` | `source_timing` |
| `/source/pulseWidth` | ns (single/periodic) | `source_pulse_width_ns` |
| `/source/pulsePeriod` | ns (periodic) | `source_pulse_period_ns` |
| `/sample/composition` | `Sym frac Sym frac ...` | `sample_composition` |
| `/sample/isotope` | `symbol mass_number atom_fraction` | one entry in `sample_isotopes` |
| `/sample/density` | g/cm3 | `sample_density` |
| `/sample/shape` | `cube \| sphere \| cylinder` | `sample_shape` |
| `/sample/size` | mm | `sample_size` |
| `/sample/height` | mm (cylinder) | `sample_height` |
| `/sample/position` | `x y z` (mm) | `sample_position` |
| `/detector/add` | `name radius_mm height_mm x y z` | one entry in `detectors` |
| `/shielding/add` | `material thickness_mm x y z` | one entry in `shielding` |
| `/output/file` | base path | `output_file` |

`/detector/add` and `/shielding/add` append one item per line, so a run can hold
several. The first `/detector/add` replaces the built-in default detector. A
detector's name labels both its volume and its output subdirectory.

`/sample/isotope` also appends one line per isotope, keyed by element symbol. It
is optional: an element with no `/sample/isotope` line uses natural isotopic
abundances. When lines are present for an element, that element is built from the
listed isotopes by atom fraction (fraction by number of atoms), which must sum to
1.0.

`/output/file` sets the base Parquet path; each detector's hits are written into
its own subdirectory, `results/<detector_name>/gamma_hits-part-NNNNN.parquet`.

## What a messenger does

<!-- Outline: registers command directories and commands; parses each command's
argument; stores the value where the geometry builder and actions can read it.
Holds no physics, only configuration state. -->

## Where values are stored

<!-- Outline: the shared configuration object the messenger writes into and the
geometry builder / actions read from. One place per configured value. -->

## Adding a command

<!-- Outline: the steps to add a new configurable value — declare the command,
parse its argument, store it, read it where it is used. Keep names snake_case to
match the Pydantic field. -->

## Relationship to the geometry and actions

<!-- Outline: the messenger only records values; geometry.md builds the world
from them and Actions.md uses them at run time. -->

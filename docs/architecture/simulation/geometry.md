# Geometry

`DetectorConstruction` builds a one-metre cubic air world and places the
configured sample, shielding slabs, and HPGe detector cylinders inside it. All
positions are in millimeters relative to the world origin.

## Sample

The sample is optional. If no `/sample/composition` command is sent, no sample
volume is created. Otherwise the engine builds a material from element mass
fractions and density, using natural isotopic abundances unless isotope entries
were supplied.

The supported shapes are:

- `cube`: `size` is the full side length;
- `sphere`: `size` is the radius;
- `cylinder`: `size` is the radius and `height` is the full height.

The sample's center is set by `/sample/position`.

## Shielding

Each `/shielding/add` command creates a square slab with a fixed 200 mm by 200 mm
footprint. Its material comes from the GEANT4 NIST material database, its depth is
the configured thickness, and its center is the configured position. A material
name that GEANT4 cannot build is skipped and reported in the log.

## Detectors

Each detector is built as a germanium cylinder with the configured radius, height,
and center. The detector volume is marked sensitive. The Python macro maps a
model detector's `dimension_mm` to the cylinder as follows:

```text
detector radius = dimension_mm.x_mm / 2
detector height = dimension_mm.z_mm
```

The model's detector type, energy resolution, and `y_mm` dimension do not yet
change the C++ geometry or response.

## Source

The General Particle Source creates the configured particle at the configured
position and sends it in the positive-z direction. Point, disk, and Gaussian beam
positions are supported. Mono-energy and text-file spectrum distributions are
supported, as are continuous, single-pulse, and periodic timing modes.

The source itself has no volume. The automatic geometry picture adds a red arrow
from the source toward the front face of the sample when a sample is present.

## Sensitive detector response

`SensitiveDetector` receives every GEANT4 step in a detector volume. It sums
positive energy deposits for the event and records one response at the earliest
deposit time. It does not record individual interaction steps or a separate count
column. `SimIO` writes the resulting energy and time values as Parquet columns.

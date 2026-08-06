# Geometry

The geometry builder constructs the simulated world from the configured values:
it places the neutron source, the sample, any shielding, and the detectors. This
is where the "swap parts without recompiling" goal is realized — the builder
reads the values the [messenger](messenger.md) stored and builds accordingly, so
the same compiled engine produces different setups.

It is built on GEANT4's `G4VUserDetectorConstruction`.

## The world

<!-- Outline: the world volume and the coordinate frame; positions are relative
to a defined origin (e.g. the sample center). -->

## Modules

Each module is built from its command group and can be varied independently.

### Source placement

<!-- Outline: how the source position/shape from /source/* is set up (point,
disk, beam). -->

### Sample

<!-- Outline: building the sample material from composition (element mass
fractions, optional isotopes), density, shape, dimensions, and placing it. -->

### Shielding

<!-- Outline: building and placing each shielding block; zero or more blocks. -->

### Detectors

<!-- Outline: building each gamma detector (type, dimensions, position) and
marking it as a sensitive detector so hits are recorded. One or more. -->

## Sensitive detectors

<!-- Outline: which volumes are sensitive, what a hit is, and how hits flow to
the output writer. Cross-reference io.md. -->

## Materials

<!-- Outline: how materials are constructed from element/isotope composition and
density; relationship to the sample composition validated on the Python side. -->

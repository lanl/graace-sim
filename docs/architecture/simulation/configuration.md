# Configuring the engine

The engine is built once and produces different experiments from GEANT4 macro
commands. The Python control layer converts a validated `Simulation` model into
that macro; the C++ program reads it at startup.

There are no Python-to-C++ bindings. The macro is the interface between the two
layers.

## Macro order

Geometry commands must be applied before `/run/initialize` because GEANT4 builds
the world during initialization. The Python macro writer uses this order:

```text
/run/numberOfThreads <count>
/sample/*                         optional
/detector/add <...>               one or more
/shielding/add <...>              optional
/output/file <path>
/run/initialize
/random/setSeeds <seed> <seed>
/source/*
/run/beamOn <neutrons>
```

The source is configured after initialization because the primary generator reads
those values when the first event is generated. A hand-written macro can use the
same pattern. `sim/macros/example.mac` is a complete batch example.

## Command groups

- `/source/*` configures particle, position, shape, energy, spectrum, and timing.
- `/sample/*` configures optional composition, isotope entries, density, shape,
  size, height, and position. Without `/sample/composition`, no sample volume is
  built.
- `/detector/add` appends one HPGe detector cylinder per line. The first line
  replaces the built-in default detector.
- `/shielding/add` appends a shielding slab per line.
- `/output/file` sets the base Parquet path. Detector subdirectories and part-file
  names are added by `SimIO`.

See the [command reference](messenger.md) for argument formats.

## Python model relationship

The Python model uses descriptive `snake_case` names and validates values before
writing commands. Some GEANT4 command names use camelCase because those are the
registered UI paths, for example `/source/energyType` and `/source/pulseWidth`.

The current model-to-engine mapping has two important limitations:

- detector `type`, `energy_resolution_kev`, and the `y_mm` detector dimension are
  accepted by Pydantic but are not sent to or used by the C++ engine;
- the engine always builds detectors as HPGe cylinders and uses half of
  `dimension_mm.x_mm` as the radius and `dimension_mm.z_mm` as the height.

Keep the generated `.mac` file with the original YAML when recording a run: it is
the exact command list sent to GEANT4.

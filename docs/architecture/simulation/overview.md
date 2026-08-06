# Simulation Engine Overview

The simulation engine is the compiled GEANT4 application that does the physics:
neutron transport, neutron capture, gamma-ray production, and detector response.
It is built once and then driven entirely by configuration — the Python control
layer writes a GEANT4 macro, the engine reads it, runs, and writes output. The
engine holds no experiment-specific values of its own.

This page is the entry point for the engine's design. The other pages cover each
part in detail:

- [configuration.md](configuration.md) — how a configuration reaches the engine.
- [messenger.md](messenger.md) — the command interface that receives it.
- [geometry.md](geometry.md) — how the source, sample, shielding, and detectors
  are built from the configured values.
- [Actions.md](Actions.md) — what happens each run, event, and step.
- [io.md](io.md) — what the engine records and how it writes output.

## Directory structure

Headers live in `sim/include/` and their implementations in `sim/src/`, one pair
per class. The tree below lists them by class rather than repeating each name in
both folders.

```
sim/
├── apps/
│   └── graace_sim_main.cc            main() — the program entry point
├── include/                          class headers (.hh)
│   ├── ActionInitialization.hh       declares the class that registers the source generator and the actions
│   ├── DetectorConstruction.hh       declares the class that builds the world from the configured values
│   ├── SensitiveDetector.hh          declares the class that records gamma hits in the detector volumes
│   ├── PrimaryGeneratorAction.hh     declares the class that produces each event's starting neutron(s)
│   ├── RunAction.hh                  declares the class that opens and closes the output per run
│   ├── EventAction.hh                declares the class that handles per-event bookkeeping
│   ├── SteppingAction.hh             declares the class that records interactions as particles move
│   ├── Messenger.hh                  declares the class that defines the /source, /sample, ... commands
│   ├── Config.hh                     declares the class that holds the configured values the engine reads
│   ├── SimIO.hh                      declares the class that writes the recorded data to Parquet
│   ├── seed.hh                       declares the class that handles the random seed
│   └── utils.hh                      declares small shared helpers
├── src/                              class implementations (.cc)
│   ├── ActionInitialization.cc       registers the source generator and the actions
│   ├── DetectorConstruction.cc       builds the world from the configured values
│   ├── SensitiveDetector.cc          records gamma hits in the detector volumes
│   ├── PrimaryGeneratorAction.cc     produces each event's starting neutron(s)
│   ├── RunAction.cc                  opens and closes the output per run
│   ├── EventAction.cc                per-event bookkeeping
│   ├── SteppingAction.cc             records interactions as particles move
│   ├── Messenger.cc                  defines the /source, /sample, ... commands
│   ├── Config.cc                     holds the configured values the engine reads
│   ├── SimIO.cc                      writes the recorded data to Parquet
│   ├── seed.cc                       random seed handling
│   └── utils.cc                      small shared helpers
├── macros/                           hand-written macros for visualization and manual runs
├── tests/                            C++ engine tests
└── CMakeLists.txt                    the build definition
```

The groupings (`geometry`, `source and actions`, …) are for reading only — the
files sit directly in `sim/src/` and `sim/include/`. Each class maps to a page in
this folder: geometry to [geometry.md](geometry.md), the actions to
[Actions.md](Actions.md), the messenger and config to [messenger.md](messenger.md),
and `SimIO` to [io.md](io.md).

## Startup (`main`)

<!-- Outline:
- create the run manager
- install the physics list (neutron-capable, e.g. FTFP_BERT_HP)
- register the geometry builder and the action set
- register the command interface (messenger)
- if given a macro, execute it; otherwise open the interactive window
-->

## Physics list

<!-- Outline: which physics list and why; high-precision neutron data;
gamma production; anything special for PGAA/NAA. -->

## Run flow

<!-- Outline: macro in -> initialize -> beamOn N -> output written.
A short numbered walk-through from macro to output file. -->

## Build

<!-- Outline: CMake + Ninja via a pixi task; how GEANT4 is found; where the
graace-sim executable lands. Cross-reference general.md. -->

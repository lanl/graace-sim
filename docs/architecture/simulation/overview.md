# Simulation engine overview

The simulation engine is the compiled GEANT4 application in `sim/`. It builds the
configured world, transports particles with the high-precision neutron physics
list, records energy deposited in detector volumes, and writes Parquet output.
The Python layer drives it by writing a GEANT4 macro.

## Source tree

```text
sim/
├── apps/
│   └── graace_sim_main.cc       program entry point
├── include/
│   ├── ActionInitialization.hh
│   ├── Config.hh
│   ├── DetectorConstruction.hh
│   ├── EventAction.hh
│   ├── GeometryPicture.hh
│   ├── Messenger.hh
│   ├── PrimaryGeneratorAction.hh
│   ├── RunAction.hh
│   ├── SensitiveDetector.hh
│   ├── SimIO.hh
│   └── utils.hh
├── src/                         implementations of the headers above
├── macros/                      hand-written macros for manual runs
└── CMakeLists.txt               build and install definition
```

There is no separate `SteppingAction`, random-seed class, or C++ test directory.
The `SensitiveDetector` receives GEANT4 steps inside detector volumes and the
`EventAction` reports progress; those classes replace the interaction-level action
suggested by older documentation.

## Startup and run flow

`graace_sim_main.cc` creates a multithreaded run manager, installs
`FTFP_BERT_HP`, registers `DetectorConstruction` and `ActionInitialization`, and
creates the `Messenger`. With a macro argument it runs in batch mode; without one
it opens the interactive UI.

Before `/run/initialize`, the macro configures geometry and the output path. The
run manager then constructs the world and marks detector volumes as sensitive.
The source is configured lazily on the first event, so `/source/*` commands can
appear after initialization. `/run/beamOn N` produces `N` neutron events.

The runner writes `/run/numberOfThreads` from `runner.cpu_percent` and sends
`/random/setSeeds` after initialization. A serial run is reproducible for a fixed
seed; multithreaded runs can differ in event ordering.

## Physics list

The engine uses GEANT4's `FTFP_BERT_HP` physics list, which includes high-precision
neutron interactions needed for neutron transport and capture gamma production.
The source is generated with GEANT4's General Particle Source.

## Actions and output

Worker threads register `PrimaryGeneratorAction`, `RunAction`, and `EventAction`.
The master registers only `RunAction`.

- `PrimaryGeneratorAction` configures particle, position, energy, and timing, then
  generates one primary vertex per event.
- `RunAction` opens thread-local `SimIO` on workers and asks the master to write the
  geometry picture at the beginning of the run.
- `EventAction` prints progress every 1000 events.
- `SensitiveDetector` sums positive energy deposits in each detector for an event
  and records one response with the total energy and earliest deposit time.
- `SimIO` writes buffered responses as detector-specific Parquet part files.

The part files are under the parent directory of `/output/file`. The Python macro
uses `results/gamma_hits.parquet` as the base path, yielding paths such as
`results/hpge/gamma_hits-part-w000-00000.parquet`. The geometry picture is written
as `results/geometry.png` when an offscreen viewer can be opened.

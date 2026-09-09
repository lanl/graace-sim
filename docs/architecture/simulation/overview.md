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
- [actions.md](actions.md) — what happens each run, event, and step.
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
│   ├── GeometryPicture.hh            declares the function that writes the picture of the setup
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
│   ├── GeometryPicture.cc            writes the picture of the setup
│   ├── SimIO.cc                      writes the recorded data to Parquet
│   ├── seed.cc                       random seed handling
│   └── utils.cc                      small shared helpers
├── macros/                           hand-written macros for visualization and manual runs
├── tests/                            C++ engine tests
└── CMakeLists.txt                    the build definition
```

Each class maps to a page in this folder: `DetectorConstruction` and
`SensitiveDetector` to [geometry.md](geometry.md); the actions to
[actions.md](actions.md); `Messenger` and `Config` to [messenger.md](messenger.md);
and `SimIO` to [io.md](io.md).

## Startup (`main`)

<!-- Outline:
- create the run manager
- install the physics list (neutron-capable, e.g. FTFP_BERT_HP)
- register the geometry builder and the action set
- register the command interface (messenger)
- if given a macro, execute it; otherwise open the interactive window
-->

The run manager is the multithreaded one: a PGAA run is many independent neutron
histories, which GEANT4 splits across worker threads so the run finishes in a
fraction of the wall-clock time. How many threads a run uses is set by the
macro's `/run/numberOfThreads` command — the Python runner computes it from a
percentage-of-cores cap (`runner.cpu_percent`, default 80), so a run never takes
more of the machine than allowed. The worker threads score hits and write their
own output; the master thread only opens the run and prints the summary.

## Physics list

<!-- Outline: which physics list and why; high-precision neutron data;
gamma production; anything special for PGAA/NAA. -->

## Run flow

<!-- Outline: macro in -> initialize -> beamOn N -> output written.
A short numbered walk-through from macro to output file. -->

## Picture of the setup

Every run writes a picture of its own setup, `geometry.png`, in the same folder as
its output file. There is nothing to switch on and nothing to tune.

It is written at the start of the run, after every command in the macro has been
applied and before the first neutron is fired, so a setup that is not what was
intended shows up straight away rather than after a long run. No particles are
fired to make it, so it cannot change a run's results.

What is in it:

| | |
|---|---|
| Blue shape | the sample |
| Grey-green shapes | the detectors, each labelled with its configured name |
| Translucent grey slabs | the shielding, labelled by material, see-through so the beam through them stays visible |
| Red arrow | the neutrons: it starts at the source and ends on the face of the sample they arrive at |
| Scale bar | a round number of centimetres, so sizes can be read off directly |

The camera angle and the zoom are worked out from the size of the setup, not set
by hand. The camera looks across the beam — never down it, which would hide
everything behind the sample — tilted slightly so the parts read as solid objects.
The zoom is the largest one at which everything that has to appear still fits,
measured in the picture's own two directions rather than against GEANT4's standard
view, which fits a sphere into the frame and so wastes the corners. Labels are
pushed outward from the middle of the setup, past the edge of the part each one
names, and any two that land on top of each other are separated.

A run writes no picture in the two cases where one would be unwanted or
duplicated: an interactive session, where the setup is already on screen, and
`sim/macros/draw_geometry.mac`, which opens its own viewer to make a picture with
particle paths in it. Both are recognised by the same rule — a viewer is already
open. If the build has no offscreen graphics driver, the run says so and carries
on without a picture.

Tracks are drawn red for neutrons and yellow-orange for gammas, the same in every
picture the engine draws.

## Build

<!-- Outline: CMake + Ninja via a pixi task; how GEANT4 is found; where the
graace-sim executable lands. Cross-reference general.md. -->

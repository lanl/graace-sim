# Actions

GEANT4 calls user actions at run and event boundaries. GRAACE-SIM registers
three worker actions and one master action through `ActionInitialization`.

## Primary generator

`PrimaryGeneratorAction` uses GEANT4's General Particle Source. On the first
event it reads the source settings from `Config` and configures the particle,
position distribution, direction, energy distribution, and timing. It then
creates the primary vertex for each event.

A point source is placed at its configured center. A disk uses a circular plane;
a beam uses GEANT4's radial beam sigma. The source direction is positive z.

## Run action

Worker `RunAction` instances open their thread-local `SimIO` writer at the start
of a run and flush it at the end. The master instance writes the geometry picture
at the beginning and prints the total event count at the end. The master does not
record detector hits.

## Event action

`EventAction` reports progress every 1000 processed events. It does not own the
hit data; the sensitive detector records the detector response.

## Sensitive detector

Each detector volume has a `SensitiveDetector`. For every event it sums positive
energy deposits in that volume. At the end of the event, if the sum is positive,
it sends one record to `SimIO` containing:

- total deposited energy in keV;
- time of the earliest deposit in ns;
- detector identity, supplied by the detector output directory.

This is an event-level detector response, not an interaction-level event log.

## Threading

The engine uses GEANT4's multithreaded run manager. Each worker has its own
`SimIO` instance and writes its own part files, so worker output does not need a
shared writer lock. The worker identifier in each filename prevents collisions.

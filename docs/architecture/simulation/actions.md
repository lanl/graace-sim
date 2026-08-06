# Actions

GEANT4 lets the engine hook into a run at several levels — the whole run, each
event, each track, and each step. The action classes are where the engine
decides what to record as neutrons and gammas move through the setup.

They are built on GEANT4's action base classes, wired together by an action
initialization class.

## Action initialization

<!-- Outline: the class that registers the primary generator and the run/event/
stepping actions with the run manager. -->

## Primary generator

<!-- Outline: how each event's starting neutron(s) are produced from the
configured source (position, energy, timing). Built on the General Particle
Source. -->

## Run action

<!-- Outline: start/end of a run — open and close the output, any per-run
setup and summary. -->

## Event action

<!-- Outline: per-event bookkeeping — what is collected per event before it is
written. -->

## Stepping action

<!-- Outline: per-step logic — detecting the interactions of interest (neutron
capture, gamma production) and passing them to the output writer. Keep this only
as detailed as the recorded quantities require. -->

## Relationship to output

<!-- Outline: the actions gather the recorded quantities; io.md defines how they
are written. Cross-reference io.md. -->

# Configuring the Engine

The engine is built once and produces different experiments depending only on
the commands it is fed. Configuration reaches it as a GEANT4 macro: a text file
of UI commands. The Python control layer writes this macro from the validated
configuration; the engine reads it at startup.

There are no Python-to-C++ bindings. The macro is the entire interface between
the two layers.

## The macro

<!-- Outline: what a macro is (a list of /command value lines), where it comes
from (Python writes it into the run folder), and a short annotated example
showing /source, /sample, /detector, /shielding, /output, /run/initialize,
/run/beamOn. -->

## Command groups

The engine registers one command group per configurable part. Each maps onto a
module built in [geometry.md](geometry.md):

- `/source/*` — the neutron source (particle, position, energy, timing).
- `/sample/*` — the assayed material (composition, density, shape, position).
- `/detector/*` — a gamma detector (type, dimensions, position, resolution).
- `/shielding/*` — a shielding block (material, thickness, placement).
- `/output/*` — what to record and where to write it.

The commands themselves are defined by the command interface — see
[messenger.md](messenger.md).

## Order of commands

<!-- Outline: which commands must come before /run/initialize (geometry and
material setup) and which come after (source, run). Why order matters. -->

## Relationship to the Pydantic models

<!-- Outline: every command corresponds to a field on a Pydantic model; the
Python side turns the validated model into these commands. Names stay
snake_case on both sides. Cross-reference python/models.md. -->

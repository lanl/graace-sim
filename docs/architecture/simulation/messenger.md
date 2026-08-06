# Command Interface (Messenger)

The command interface defines the GEANT4 UI commands the engine understands —
the `/source/*`, `/sample/*`, `/detector/*`, `/shielding/*`, and `/output/*`
groups listed in [configuration.md](configuration.md). It is the piece that
turns a line of a macro into a stored value the rest of the engine reads.

It is built on GEANT4's `G4UImessenger`.

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

# Output (IO)

The engine records what happens in the detectors and writes it to disk. Output
is written as Parquet files, stored with the run configuration so every run
carries the exact settings that produced it. The primary recorded quantity is
the gamma-emission data — the energies and counts seen by each detector — from
which spectra, sensitivity, and minimum-flux estimates are built.

## What is recorded

<!-- Outline: the recorded quantities per gamma hit (e.g. detector, energy,
time), and any other tables. Define the columns and their units. -->

## File format

<!-- Outline: Parquet, one file per table; where files land (the run's output
directory); filenames. Cross-reference general.md. -->

## The run configuration alongside the output

<!-- Outline: the validated configuration is stored with the output so the run
is self-describing and reproducible. (How it is stored is decided elsewhere; do
not pin it here.) -->

## Writing during a run

<!-- Outline: how the writer is opened per run, appended to as events are
processed, and closed; threading considerations if multithreaded. -->

## Reading the output

<!-- Outline: how the Python side reads Parquet back for analysis; the columns
map to the recorded quantities above. -->

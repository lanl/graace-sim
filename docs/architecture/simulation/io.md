# Output (IO)

The engine records what happens in the detectors and writes it to disk. Output
is written as Parquet files, stored with the run configuration so every run
carries the exact settings that produced it. The primary recorded quantity is
the gamma-emission data — the energies and counts seen by each detector — from
which spectra, sensitivity, and minimum-flux estimates are built.

## What is recorded

<!-- Outline: the recorded quantities per gamma hit (energy in keV, time in ns),
and any other tables. Define the columns and their units. The detector is not a
column: each detector's hits are written to its own subdirectory, so the
directory name identifies the detector. -->

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

The engine runs multithreaded, so several worker threads record hits at once. The
writer (`SimIO`) is thread-local: each worker owns its own buffers and writes its
own Parquet part files, so nothing is shared and the hit path needs no locking.
Each worker's part files carry a `w<thread>` tag in the name
(`gamma_hits-part-w000-00000.parquet`) so two workers never target the same file.
The master thread scores no hits — it only opens the run and prints the final
summary. Because a detector's whole set of part files is read back as one table,
the number of worker threads is transparent to the reader; row order across
threads is not fixed, but the set of hits is complete.

## Reading the output

<!-- Outline: how the Python side reads Parquet back for analysis; the columns
map to the recorded quantities above. -->

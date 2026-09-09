"""Plot the gamma spectrum of one or more finished runs.

    python examples/scripts/plot_spectrum.py data/dd_no_moderator_000 [...]

For each run directory given, reads every detector's Parquet files, adds them
into one spectrum, and writes ``spectrum.png`` next to the results inside that
run directory.

The engine records the energy each detector collected in each event, exactly,
with no measurement error. A real germanium detector spreads a single energy
over a small range of readings instead, so a measured peak has width. This
script adds that width back before histogramming, which is why the peaks here
look like a real spectrum rather than single spikes.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Write image files; never try to open a window.

import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq
from loguru import logger

# The histogram covers 0 to 12 MeV in 2 keV bins. That top end holds the whole
# range the engine can produce here, including the high-energy gammas a
# 14.1 MeV neutron makes.
BIN_WIDTH_KEV = 2.0
MAX_ENERGY_KEV = 12_000.0

# How much a germanium detector spreads a single energy, as the full width at
# half maximum of the spread. Detectors are specified by their width at
# 1332 keV, the reference line used for the purpose, and the width grows as the
# square root of energy: width = REFERENCE_WIDTH * sqrt(energy / 1332).
REFERENCE_WIDTH_KEV = 2.0
REFERENCE_ENERGY_KEV = 1332.0

# Gamma energies worth marking on every plot, and where each comes from. These
# are labelled whether or not the run produced them, because a line that is
# missing is as informative as one that is present: 2223 keV appears only once a
# moderator has slowed the neutrons down, and 4439 keV comes from the carbon in
# the moderator itself rather than from the sample.
MARKED_LINES = {
    511: "511 positron",
    847: "847 iron, scattered",
    2223: "2223 hydrogen, absorbed",
    4439: "4439 carbon, scattered",
}


def read_energies(run_directory: Path) -> np.ndarray:
    """Every recorded energy in a run, in keV, from all of its detectors.

    The engine writes one directory per detector and one file per worker thread
    inside it, so this collects every file under ``results/``. The two detectors
    in these runs are placed symmetrically, so adding them together just doubles
    the counts for the same number of neutrons.
    """
    files = sorted((run_directory / "results").glob("*/*.parquet"))
    if not files:
        raise FileNotFoundError(f"no Parquet results found under {run_directory}")
    energies = [pq.read_table(f, columns=["energy"])["energy"].to_numpy() for f in files]
    return np.concatenate(energies)


def add_detector_width(energies: np.ndarray) -> np.ndarray:
    """Spread each energy the way a real germanium detector would.

    Shifts every reading by a random amount drawn from a bell curve whose width
    grows as the square root of the energy, so the peaks come out with the width
    a measured spectrum has.
    """
    fwhm = REFERENCE_WIDTH_KEV * np.sqrt(
        np.maximum(energies, 0.0) / REFERENCE_ENERGY_KEV
    )
    # A bell curve's full width at half maximum is about 2.355 times the
    # standard deviation the random draw needs.
    spread = fwhm / 2.355
    return energies + np.random.default_rng(0).normal(0.0, spread)


def plot_spectrum(run_directory: Path) -> Path:
    """Write ``spectrum.png`` for one run directory and return its path."""
    energies = add_detector_width(read_energies(run_directory))

    edges = np.arange(0.0, MAX_ENERGY_KEV + BIN_WIDTH_KEV, BIN_WIDTH_KEV)
    counts, _ = np.histogram(energies, bins=edges)
    centers = edges[:-1] + BIN_WIDTH_KEV / 2

    figure, axes = plt.subplots(figsize=(9, 4.5))
    axes.step(centers, counts, where="mid", linewidth=0.7, color="#0055A2")
    axes.set_xlabel("Gamma energy (keV)")
    axes.set_ylabel(f"Counts per {BIN_WIDTH_KEV:.0f} keV")
    axes.set_title(run_directory.name)
    # Counts fall off steeply with energy, so a log scale is the only way the
    # high-energy end is visible at all next to the low-energy peaks.
    axes.set_yscale("log")
    axes.set_xlim(0, MAX_ENERGY_KEV)
    axes.set_ylim(bottom=0.7)
    axes.grid(True, which="major", linewidth=0.3, alpha=0.5)

    # Mark the named energies. The label sits just under the top of the plot so
    # it clears the spectrum, and every run gets the same set of labels in the
    # same places so the four plots can be read against each other.
    top = axes.get_ylim()[1]
    for energy, label in MARKED_LINES.items():
        axes.axvline(energy, color="#B03A2E", linewidth=0.6, linestyle="--", alpha=0.7)
        axes.annotate(
            label,
            xy=(energy, top),
            xytext=(3, -4),
            textcoords="offset points",
            rotation=90,
            va="top",
            ha="left",
            fontsize=7,
            color="#B03A2E",
        )

    figure.tight_layout()

    image_path = run_directory / "spectrum.png"
    figure.savefig(image_path, dpi=200)
    plt.close(figure)

    logger.info(
        "{}: {} recorded gammas -> {}", run_directory.name, len(energies), image_path
    )
    return image_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot the gamma spectrum of one or more finished runs."
    )
    parser.add_argument(
        "run_directories",
        type=Path,
        nargs="+",
        help="Run directories to plot, for example data/dd_no_moderator_000.",
    )
    args = parser.parse_args()
    for directory in args.run_directories:
        plot_spectrum(directory)

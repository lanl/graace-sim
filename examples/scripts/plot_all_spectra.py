"""Plot all four generator-comparison spectra together on one set of axes.

    python examples/scripts/plot_all_spectra.py

Reads the four runs the generator comparison is made of and draws all four
spectra on the same axes, so they can be read directly against one another.
Writes ``data/generator_comparison.png``.

All four runs fired the same number of neutrons, so the curves are directly
comparable as they stand: a higher curve means more recorded gammas, not a
different scale.

Reading and detector width come from plot_spectrum.py, which also writes the
individual per-run plots.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Write image files; never try to open a window.

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

from plot_spectrum import (
    BIN_WIDTH_KEV,
    add_detector_width,
    read_energies,
)

WORKING_DIRECTORY = Path("data")
OUTPUT_FILE = WORKING_DIRECTORY / "generator_comparison.png"

# Highest energy shown. The spectra run higher than this, but above 8 MeV there
# are only a few counts per bin and no named line, so the extra width would only
# squeeze the part of the plot that has something in it.
TOP_ENERGY_KEV = 8000.0

# The four runs, ordered so the busiest spectrum is drawn first and the sparsest
# last. Drawn the other way round, the two 14.1 MeV runs cover almost the whole
# plot and bury the 2.45 MeV curves underneath them.
#
# Each colour was checked for being distinguishable from the other three, both
# in normal colour vision and under colour blindness. The four are not
# interchangeable with any other four: see the note at the bottom of this file.
RUNS = [
    ("dt_with_moderator", "DT 14.1 MeV, 50 mm polyethylene", "#4a3aa7"),
    ("dt_no_moderator", "DT 14.1 MeV, no moderator", "#eb6834"),
    ("dd_with_moderator", "DD 2.45 MeV, 50 mm polyethylene", "#1baf7a"),
    ("dd_no_moderator", "DD 2.45 MeV, no moderator", "#2a78d6"),
]

# Chart chrome. Text stays in ink colours rather than taking a curve's colour.
SURFACE = "#ffffff"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
GRIDLINE = "#e1e0d9"

# Text sizes, set by what the printed poster needs rather than by eye.
#
# The figure is drawn 7.5 in wide and placed on the poster 15 in wide, so
# everything in it is printed at twice the size set here. The poster's body text
# is 0.38 in tall, which is 27 pt, so text that has to read as easily as the body
# text is set at half of that, near 14 pt. Anything smaller than 11 pt here
# prints below 0.3 in and is what made the first version hard to read.
#
# Scale these together if the poster ever gives the figure a different width:
# halve them for a 30 in placement, double them for 7.5 in.
KEY_SIZE = 14.0  # the key, which is where the reader gets the comparison
AXIS_TITLE_SIZE = 16.0
TICK_SIZE = 15.0
TITLE_SIZE = 18.0


def main() -> Path:
    figure, axes = plt.subplots(figsize=(7.5, 4.8), facecolor=SURFACE)
    axes.set_facecolor(SURFACE)

    edges = np.arange(0.0, TOP_ENERGY_KEV + BIN_WIDTH_KEV, BIN_WIDTH_KEV)
    centers = edges[:-1] + BIN_WIDTH_KEV / 2

    for depth, (run_id, label, colour) in enumerate(RUNS):
        run_directory = WORKING_DIRECTORY / f"{run_id}_000"
        energies = add_detector_width(read_energies(run_directory))
        counts, _ = np.histogram(energies, bins=edges)
        # A spectrum has thousands of bins, so the line is kept hairline-thin;
        # any heavier and four of them together fill in as a solid block.
        axes.step(
            centers,
            counts,
            where="mid",
            linewidth=0.6,
            color=colour,
            zorder=2 + depth,
            label=f"{label}  ({len(energies):,})",
        )
        logger.info("{}: {:,} recorded gammas", run_directory.name, len(energies))

    # Counts fall off steeply with energy, so a log scale is the only way the
    # high-energy end is visible at all next to the low-energy peaks. The top of
    # the range sits about a decade above the tallest peak, which leaves the
    # upper right corner clear for the key.
    axes.set_yscale("log")
    axes.set_ylim(0.7, 2.0e6)
    axes.set_xlim(0, TOP_ENERGY_KEV)
    axes.set_xticks(np.arange(0.0, TOP_ENERGY_KEV + 1, 2000.0))
    axes.grid(True, which="major", linewidth=0.4, color=GRIDLINE)
    axes.set_axisbelow(True)
    axes.tick_params(labelsize=TICK_SIZE, colors=SECONDARY_INK)
    axes.tick_params(which="minor", length=1.5)
    for spine in axes.spines.values():
        spine.set_color(GRIDLINE)

    axes.set_xlabel("Gamma energy (keV)", fontsize=AXIS_TITLE_SIZE, color=PRIMARY_INK)
    axes.set_ylabel(
        f"Counts per {BIN_WIDTH_KEV:.0f} keV", fontsize=AXIS_TITLE_SIZE, color=PRIMARY_INK
    )
    axes.set_title(
        "Iron sample, 10 million neutrons per run",
        fontsize=TITLE_SIZE,
        color=PRIMARY_INK,
        pad=10,
    )

    # The key names each curve, with its total in brackets, so the comparison is
    # quantitative and not left to the reader's eye. It is ordered brightest
    # generator first, which is the reverse of the drawing order.
    legend = axes.legend(
        handles=axes.get_legend_handles_labels()[0][::-1],
        labels=axes.get_legend_handles_labels()[1][::-1],
        loc="upper right",
        fontsize=KEY_SIZE,
        facecolor=SURFACE,
        edgecolor=GRIDLINE,
        framealpha=1.0,
        borderpad=0.5,
        handlelength=1.6,
        handletextpad=0.6,
        labelspacing=0.35,
    )
    legend.set_zorder(10)
    for text in legend.get_texts():
        text.set_color(SECONDARY_INK)

    # Poster-sized text needs more of the figure than small text did: the margins
    # are what the axis titles and the tick labels actually take up. The right
    # margin leaves room for the last tick label, which otherwise runs off the
    # edge of the figure.
    figure.subplots_adjust(left=0.135, right=0.945, top=0.900, bottom=0.150)
    figure.savefig(OUTPUT_FILE, dpi=300, facecolor=SURFACE)
    plt.close(figure)

    logger.info("Wrote {}", OUTPUT_FILE)
    return OUTPUT_FILE


# On the four colours: with four curves crossing each other everywhere, every
# pair has to be tellable apart, not just neighbouring pairs. Of the 70 ways to
# pick four colours from the reference set of eight, only 11 clear that bar, and
# these four have the best contrast on a white page of any of the 11. The green
# is the one weak point at 2.7:1 against 3:1 wanted, which is why every curve is
# also named with its total in the key rather than by colour alone.

if __name__ == "__main__":
    main()

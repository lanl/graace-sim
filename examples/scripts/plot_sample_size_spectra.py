"""Plot all eight sample spectra together on one set of axes.

    python examples/scripts/plot_sample_size_spectra.py

Eight runs: the two generator energies, with and without a polyethylene
moderator, each with the full-size iron cylinder (radius 25 mm, height 40 mm)
and with the same cylinder five times smaller in every direction. Writes
``data/sample_size_spectra.png``.

Every run fired ten million neutrons with the same seed, so the curves are
directly comparable as they stand: a higher curve means more recorded gammas.

Each condition keeps its colour from the generator comparison plot. The
full-size run is the strong tone and the small run the pale tone of that same
colour, so a pair of curves in one colour is one condition at two sample sizes,
and the vertical gap between them is what the extra iron did.

The four no-sample background runs are not on this plot; they are what
plot_self_shielding.py subtracts. That matters for reading the two moderated
pairs, whose gap is much narrower than the others: most of what the detectors
record in those runs comes from the moderator slab rather than the sample, and
that part is the same in both sizes, so it pushes both curves up together and
closes the gap between them.

Reading and detector width come from plot_spectrum.py.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Write image files; never try to open a window.

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
from matplotlib.legend_handler import HandlerTuple

from plot_spectrum import BIN_WIDTH_KEV, add_detector_width, read_energies

WORKING_DIRECTORY = Path("data")
OUTPUT_FILE = WORKING_DIRECTORY / "sample_size_spectra.png"

# Same upper limit as the generator comparison, for the same reason: above 8 MeV
# there are only a few counts per bin, and the extra width would squeeze the part
# of the plot that has something in it.
TOP_ENERGY_KEV = 8000.0

# The four conditions in the colours the generator comparison plot gave them, so
# a colour means the same thing on both figures. The second colour in each row is
# the same hue mixed halfway with white, for the small-sample run.
CONDITIONS = [
    ("dt_with_moderator", "DT 14.1 MeV, 50 mm polyethylene", "#4a3aa7", "#9a8fd8"),
    ("dt_no_moderator", "DT 14.1 MeV, no moderator", "#eb6834", "#f7b394"),
    ("dd_with_moderator", "DD 2.45 MeV, 50 mm polyethylene", "#1baf7a", "#7ddcba"),
    ("dd_no_moderator", "DD 2.45 MeV, no moderator", "#2a78d6", "#93c1f2"),
]

SURFACE = "#ffffff"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
GRIDLINE = "#e1e0d9"

# Text sizes, set by what the printed poster needs rather than by eye. The figure
# is drawn 7.5 in wide and placed on the poster 15 in wide, so everything prints
# at twice the size set here; 11 pt is the floor that still prints at 0.3 in.
KEY_SIZE = 12.0
AXIS_TITLE_SIZE = 16.0
TICK_SIZE = 15.0
TITLE_SIZE = 18.0


def main() -> Path:
    figure, axes = plt.subplots(figsize=(7.5, 4.8), facecolor=SURFACE)
    axes.set_facecolor(SURFACE)

    edges = np.arange(0.0, TOP_ENERGY_KEV + BIN_WIDTH_KEV, BIN_WIDTH_KEV)
    centers = edges[:-1] + BIN_WIDTH_KEV / 2

    pairs = []
    labels = []
    for depth, (condition, condition_label, strong, pale) in enumerate(CONDITIONS):
        drawn = []
        # Full size first so the small run is drawn on top of it: the small run is
        # the lower curve of the two, and underneath it disappears.
        for suffix, colour, weight in [("", strong, 0.7), ("_small_sample", pale, 0.9)]:
            energies = add_detector_width(
                read_energies(WORKING_DIRECTORY / f"{condition}{suffix}_000")
            )
            counts, _ = np.histogram(energies, bins=edges)
            # A spectrum has hundreds of bins, so the line is kept hairline-thin;
            # any heavier and eight of them together fill in as a solid block. The
            # pale tones get a fraction more weight, which is what it takes for
            # them to carry as far on a printed page as the strong ones.
            #
            # Partly transparent, so that where curves cross, both are still
            # visible and the crossing itself shows as a darker patch instead of
            # whichever one happened to be drawn last simply winning.
            line = axes.step(
                centers,
                counts,
                where="mid",
                linewidth=weight,
                color=colour,
                alpha=0.75,
                zorder=2 + depth,
            )[0]
            drawn.append(line)
            logger.info(
                "{}{}: {:,} recorded gammas", condition, suffix, len(energies)
            )

        # One key entry per condition rather than per run, with both tones in its
        # swatch, left to right in the order the title names them.
        pairs.append(tuple(drawn))
        labels.append(condition_label)

    # Counts fall off steeply with energy, so a log scale is the only way the
    # high-energy end is visible at all next to the low-energy peaks. The top of
    # the range is set just above the tallest bin of any run, which is the pile-up
    # below 100 keV; the key then fits in the upper right corner because above
    # 2.5 MeV no curve comes near the top.
    axes.set_yscale("log")
    axes.set_ylim(0.7, 5.0e5)
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
        "Iron sample at two sizes, 10 million neutrons",
        fontsize=TITLE_SIZE,
        color=PRIMARY_INK,
        pad=10,
    )

    # The swatch is the two tones side by side, and the title reads across them in
    # the same order, so the key says which tone is which size without needing a
    # sentence of explanation.
    legend = axes.legend(
        pairs[::-1],
        labels[::-1],
        title="full size  /  small sample",
        handler_map={tuple: HandlerTuple(ndivide=None, pad=0.0)},
        loc="upper right",
        fontsize=KEY_SIZE,
        facecolor=SURFACE,
        edgecolor=GRIDLINE,
        framealpha=1.0,
        borderpad=0.5,
        handlelength=3.0,
        handletextpad=0.6,
        labelspacing=0.35,
    )
    legend.set_zorder(10)
    legend.get_title().set_fontsize(KEY_SIZE)
    legend.get_title().set_color(SECONDARY_INK)
    for text in legend.get_texts():
        text.set_color(SECONDARY_INK)

    figure.subplots_adjust(left=0.135, right=0.945, top=0.900, bottom=0.150)
    figure.savefig(OUTPUT_FILE, dpi=300, facecolor=SURFACE)
    plt.close(figure)

    logger.info("Wrote {}", OUTPUT_FILE)
    return OUTPUT_FILE


if __name__ == "__main__":
    main()

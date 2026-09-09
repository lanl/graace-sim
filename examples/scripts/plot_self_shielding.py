"""Plot how much a large sample distorts its own gamma spectrum.

    python examples/scripts/plot_self_shielding.py

For each of the four generator-and-moderator conditions there are three runs of
ten million neutrons: one with the full-size iron cylinder (radius 25 mm, height
40 mm), one with the same cylinder scaled down five times in every direction, and
one with no sample at all. Writes ``data/self_shielding.png``.

What the plot shows. Gammas made inside a large sample have to get out through
the rest of the iron, which both absorbs them and scatters them down in energy.
So a large sample does not simply record fewer counts than a small one; it
records a softer spectrum, with counts moved out of the high-energy lines and
into the low-energy continuum. Scaling each spectrum to its own total takes the
overall count rate out of the comparison and leaves only that change in shape.

A ratio above one means the small sample holds a larger share of its counts at
that energy than the full-size sample does, which is the same as saying the
full-size sample lost counts there. The ratio rises with energy, so the loss is
worst for exactly the high-energy lines a measurement would want to use.

The no-sample runs are subtracted first. Without that step the two moderated
conditions would be measuring the polyethylene slab rather than the sample: the
slab and the neutrons scattering off it account for 68% of what the detectors
record in the full-size DD run with a moderator, and 93% in the small-sample one.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Write image files; never try to open a window.

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

from plot_spectrum import add_detector_width, read_energies

WORKING_DIRECTORY = Path("data")
OUTPUT_FILE = WORKING_DIRECTORY / "self_shielding.png"

# Wide bins, because this is a ratio of two measured numbers and the fine
# structure of the spectrum is not what is being shown. At 100 keV the quietest
# band still holds enough counts for the ratio to mean something.
BIN_WIDTH_KEV = 100.0
TOP_ENERGY_KEV = 8000.0

# Above this relative uncertainty a point says nothing, so it is left out rather
# than drawn as noise the reader has to discount.
WORST_USABLE_ERROR = 0.10

# The same four colours, in the same order, as the generator comparison plot, so
# a colour means the same condition everywhere on the poster.
CONDITIONS = [
    ("dt_with_moderator", "DT 14.1 MeV, 50 mm polyethylene", "#4a3aa7"),
    ("dt_no_moderator", "DT 14.1 MeV, no moderator", "#eb6834"),
    ("dd_with_moderator", "DD 2.45 MeV, 50 mm polyethylene", "#1baf7a"),
    ("dd_no_moderator", "DD 2.45 MeV, no moderator", "#2a78d6"),
]

SURFACE = "#ffffff"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
GRIDLINE = "#e1e0d9"

# Text sizes, set by what the printed poster needs. See plot_all_spectra.py for
# where these numbers come from; they are the same figure width on the poster.
KEY_SIZE = 14.0
AXIS_TITLE_SIZE = 16.0
TICK_SIZE = 15.0
TITLE_SIZE = 18.0


def counts(run_directory: Path, edges: np.ndarray) -> np.ndarray:
    """Histogram one run's recorded gamma energies."""
    energies = add_detector_width(read_energies(WORKING_DIRECTORY / run_directory))
    binned, _ = np.histogram(energies, bins=edges)
    return binned.astype(float)


def main() -> Path:
    figure, axes = plt.subplots(figsize=(7.5, 4.8), facecolor=SURFACE)
    axes.set_facecolor(SURFACE)

    edges = np.arange(0.0, TOP_ENERGY_KEV + BIN_WIDTH_KEV, BIN_WIDTH_KEV)
    centers = edges[:-1] + BIN_WIDTH_KEV / 2

    for condition, label, colour in CONDITIONS:
        # All three runs fired the same number of neutrons, so the no-sample run
        # subtracts directly with no scaling.
        background = counts(Path(f"{condition}_no_sample_000"), edges)
        full = counts(Path(f"{condition}_000"), edges) - background
        small = counts(Path(f"{condition}_small_sample_000"), edges) - background

        # Scaling each spectrum to its own total is what removes the difference in
        # count rate and leaves only the difference in shape.
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = (small / small.sum()) / (full / full.sum())
            # Poisson on each of the four measured numbers that go into a point.
            raw_full = counts(Path(f"{condition}_000"), edges)
            raw_small = counts(Path(f"{condition}_small_sample_000"), edges)
            error = ratio * np.sqrt(
                (raw_small + background) / np.square(small)
                + (raw_full + background) / np.square(full)
            )

        usable = np.isfinite(ratio) & (ratio > 0) & (error / ratio < WORST_USABLE_ERROR)
        axes.plot(
            centers[usable],
            ratio[usable],
            linewidth=1.8,
            color=colour,
            label=label,
        )
        logger.info(
            "{}: {} of {} bins usable, ratio {:.2f} at 200 keV to {:.2f} at 4 MeV",
            condition,
            int(usable.sum()),
            len(centers),
            ratio[2],
            ratio[40],
        )

    # One is where the two samples hold the same share of their counts, so any
    # departure from this line is the full-size sample distorting its spectrum.
    axes.axhline(1.0, linewidth=1.0, color=SECONDARY_INK, zorder=1)

    axes.set_xlim(0, TOP_ENERGY_KEV)
    axes.set_ylim(0.6, 2.0)
    axes.set_xticks(np.arange(0.0, TOP_ENERGY_KEV + 1, 2000.0))
    axes.grid(True, which="major", linewidth=0.4, color=GRIDLINE)
    axes.set_axisbelow(True)
    axes.tick_params(labelsize=TICK_SIZE, colors=SECONDARY_INK)
    for spine in axes.spines.values():
        spine.set_color(GRIDLINE)

    axes.set_xlabel("Gamma energy (keV)", fontsize=AXIS_TITLE_SIZE, color=PRIMARY_INK)
    axes.set_ylabel("Small sample / full size", fontsize=AXIS_TITLE_SIZE, color=PRIMARY_INK)
    axes.set_title(
        "A large sample softens its own gamma spectrum",
        fontsize=TITLE_SIZE,
        color=PRIMARY_INK,
        pad=10,
    )

    # Lower right, which is the one corner no curve reaches: every condition sits
    # above one from about 400 keV upwards.
    legend = axes.legend(
        loc="lower right",
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

    figure.subplots_adjust(left=0.135, right=0.945, top=0.900, bottom=0.150)
    figure.savefig(OUTPUT_FILE, dpi=300, facecolor=SURFACE)
    plt.close(figure)

    logger.info("Wrote {}", OUTPUT_FILE)
    return OUTPUT_FILE


if __name__ == "__main__":
    main()

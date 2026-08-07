"""Write the GEANT4 macro from a validated ``Simulation``.

The macro is the only interface between the Python layer and the engine: there
are no Python-to-C++ bindings. This module turns a validated ``Simulation`` into
the ordered list of GEANT4 UI commands the engine reads (the ``/source/*``,
``/sample/*``, ``/detector/*``, ``/shielding/*``, and ``/output/*`` groups
registered in ``sim/src/Messenger.cc``) and writes them to the run's macro file.

The engine builds every feature the models describe, so each field maps to a
command directly — there is nothing to reject. Command order matches
``sim/macros/example.mac``: geometry and materials before ``/run/initialize``,
the source and the run after.
"""

import os
from pathlib import Path

from loguru import logger

from models.simulation import Simulation


def _format(value: float) -> str:
    """Format a number with minimal digits (no trailing zeros)."""
    text = f"{value:.12f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _thread_count(cpu_percent: int) -> int:
    """How many engine threads to run: a fraction of the machine's cores.

    ``threads = max(1, floor(cores * cpu_percent / 100))`` using the machine's
    logical cores (``os.cpu_count()``), so a run uses only the configured
    fraction of the machine and always at least one thread. Falls back to one
    core if the count is unknown.
    """
    cores = os.cpu_count() or 1
    return max(1, cores * cpu_percent // 100)


def _vector(x_mm: float, y_mm: float, z_mm: float) -> str:
    """Format a position as ``x y z`` for a ``/.../position`` command."""
    return f"{_format(x_mm)} {_format(y_mm)} {_format(z_mm)}"


def _sample_commands(simulation: Simulation) -> list[str]:
    """The ``/sample/*`` commands. Empty when the setup has no sample."""
    sample = simulation.sample
    if sample is None:
        return []

    composition = " ".join(
        f"{element.symbol} {_format(element.mass_fraction)}"
        for element in sample.composition.elements
    )
    position = sample.position_mm
    commands = [f"/sample/composition {composition}"]
    # An isotope breakdown is optional per element; without one the engine uses
    # natural abundances and no /sample/isotope line is written.
    for element in sample.composition.elements:
        if element.isotopes is None:
            continue
        for isotope in element.isotopes:
            commands.append(
                f"/sample/isotope {element.symbol} {isotope.mass_number} "
                f"{_format(isotope.atom_fraction)}"
            )
    commands += [
        f"/sample/density {_format(sample.composition.density_g_cm3)}",
        f"/sample/shape {sample.shape}",
        f"/sample/size {_format(sample.size_mm)}",
    ]
    if sample.shape == "cylinder":
        commands.append(f"/sample/height {_format(sample.height_mm)}")
    commands.append(
        f"/sample/position {_vector(position.x_mm, position.y_mm, position.z_mm)}"
    )
    return commands


def _detector_commands(simulation: Simulation) -> list[str]:
    """One ``/detector/add`` per detector.

    The engine builds each detector as a cylinder, so the model's box
    ``dimension_mm`` maps to a crystal radius and height: the radius is half the
    x side and the height is the z side (the inverse of the mapping documented
    in ``examples/yaml_files/example.yaml``). The name labels the detector's
    volume and the subdirectory its hits are written to.
    """
    commands = []
    for detector in simulation.detectors:
        dimension = detector.dimension_mm
        position = detector.position_mm
        radius = _format(dimension.x_mm / 2)
        height = _format(dimension.z_mm)
        commands.append(
            f"/detector/add {detector.name} {radius} {height} "
            f"{_vector(position.x_mm, position.y_mm, position.z_mm)}"
        )
    return commands


def _shielding_commands(simulation: Simulation) -> list[str]:
    """One ``/shielding/add`` per shielding block."""
    commands = []
    for block in simulation.shielding:
        position = block.position_mm
        commands.append(
            f"/shielding/add {block.material} {_format(block.thickness_mm)} "
            f"{_vector(position.x_mm, position.y_mm, position.z_mm)}"
        )
    return commands


def _output_commands(simulation: Simulation) -> list[str]:
    """The ``/output/*`` command: the base path for the gamma hit Parquet files.

    The engine writes each detector's hits into its own subdirectory of the
    results directory (``results/<detector_name>/gamma_hits-part-NNNNN.parquet``),
    so this is only the base path — the detector name is added by the engine.
    """
    hits_file = simulation.environment.results_directory / "gamma_hits.parquet"
    return [f"/output/file {hits_file}"]


def _source_commands(simulation: Simulation) -> list[str]:
    """The ``/source/*`` commands: particle, position/shape, energy, timing."""
    source = simulation.source
    position = source.position
    energy = source.energy
    timing = source.timing

    center = position.center_mm
    commands = [
        f"/source/particle {source.particle}",
        f"/source/position {_vector(center.x_mm, center.y_mm, center.z_mm)}",
        f"/source/shape {position.shape}",
    ]
    if position.radius_mm is not None:
        commands.append(f"/source/radius {_format(position.radius_mm)}")

    commands.append(f"/source/energyType {energy.type}")
    if energy.type == "mono":
        commands.append(f"/source/energy {_format(energy.mono_mev)}")
    else:
        commands.append(f"/source/spectrumFile {energy.spectrum_file}")

    commands.append(f"/source/timing {timing.mode}")
    if timing.mode in {"single", "periodic"}:
        commands.append(f"/source/pulseWidth {_format(timing.pulse_width_ns)}")
    if timing.mode == "periodic":
        commands.append(f"/source/pulsePeriod {_format(timing.pulse_period_ns)}")
    return commands


def _macro_commands(simulation: Simulation) -> list[str]:
    """Assemble the full command list in the order the engine expects."""
    commands: list[str] = []
    # The thread count must be set before /run/initialize, so it leads the macro.
    threads = _thread_count(simulation.runner.cpu_percent)
    commands.append(f"/run/numberOfThreads {threads}")
    commands.extend(_sample_commands(simulation))
    commands.extend(_detector_commands(simulation))
    commands.extend(_shielding_commands(simulation))
    commands.extend(_output_commands(simulation))
    commands.append("/run/initialize")
    # Seed the random number generator so a run is reproducible: the same seed
    # gives the same output. GEANT4's built-in command takes two seeds; using the
    # one configured value for both is enough to fix the run. Under the
    # multithreaded run manager GEANT4 derives each worker's seeds from this, so
    # this is the single control for the whole run.
    commands.append(f"/random/setSeeds {simulation.run.seed} {simulation.run.seed}")
    commands.extend(_source_commands(simulation))
    commands.append(f"/run/beamOn {simulation.run.neutrons}")
    return commands


def write_macro(simulation: Simulation) -> Path:
    """Write the GEANT4 macro for a validated ``Simulation`` and return its path.

    Creates the run directory and writes the macro to
    ``simulation.environment.macro_file``.
    """
    macro_path = simulation.environment.macro_file
    macro_path.parent.mkdir(parents=True, exist_ok=True)

    commands = _macro_commands(simulation)
    macro_path.write_text("\n".join(commands) + "\n", encoding="utf-8")

    logger.info("Wrote macro to {}", macro_path)
    return macro_path

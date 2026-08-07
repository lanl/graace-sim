"""The macro writer: the example config writes the expected commands in order,
and each richer source/detector/shielding feature emits its command."""

from pathlib import Path

import pytest

from config import macro as macro_module
from config.macro import _thread_count, write_macro
from config.yaml_io import load_simulation
from models.simulation import Simulation

EXAMPLE = Path(__file__).parents[2] / "examples" / "yaml_files" / "example.yaml"


def _write(simulation: Simulation, tmp_path: Path) -> list[str]:
    """Write the macro under tmp_path and return its lines."""
    simulation.environment.working_directory = tmp_path
    macro_path = write_macro(simulation)
    assert macro_path == simulation.environment.macro_file
    assert macro_path.exists()
    return macro_path.read_text().splitlines()


def test_example_commands(tmp_path):
    lines = _write(load_simulation(EXAMPLE), tmp_path)

    # Sample, detector, source, and run commands from the example config. The
    # 60 x 60 x 50 mm box maps to a crystal of radius 30 and height 50.
    assert "/sample/composition Fe 1" in lines
    assert "/sample/density 7.87" in lines
    assert "/sample/shape cylinder" in lines
    assert "/sample/height 20" in lines
    assert "/detector/add hpge 30 50 0 80 0" in lines
    assert "/source/particle neutron" in lines
    assert "/source/energyType mono" in lines
    assert "/source/energy 14.1" in lines
    assert "/source/timing continuous" in lines
    assert "/run/beamOn 10000" in lines


def test_no_isotope_command_by_default(tmp_path):
    lines = _write(load_simulation(EXAMPLE), tmp_path)
    assert not any(line.startswith("/sample/isotope") for line in lines)


def test_isotope_commands_emitted(tmp_path):
    simulation = load_simulation(EXAMPLE)
    element = simulation.sample.composition.elements[0]
    element.isotopes = [
        {"mass_number": 235, "atom_fraction": 0.9},
        {"mass_number": 238, "atom_fraction": 0.1},
    ]
    lines = _write(simulation, tmp_path)

    isotope_lines = [line for line in lines if line.startswith("/sample/isotope")]
    assert isotope_lines == [
        f"/sample/isotope {element.symbol} 235 0.9",
        f"/sample/isotope {element.symbol} 238 0.1",
    ]
    # Isotope lines follow /sample/composition and precede /run/initialize.
    composition = next(i for i, l in enumerate(lines) if l.startswith("/sample/composition"))
    initialize = lines.index("/run/initialize")
    assert composition < lines.index(isotope_lines[0]) < initialize


def test_no_sample_writes_no_sample_commands(tmp_path):
    simulation = load_simulation(EXAMPLE)
    simulation.sample = None
    lines = _write(simulation, tmp_path)

    # The sample is optional: with none set, no /sample/* command is written and
    # the engine builds no sample volume. The rest of the run is unaffected.
    assert not any(line.startswith("/sample/") for line in lines)
    assert "/detector/add hpge 30 50 0 80 0" in lines
    assert "/run/initialize" in lines
    assert "/source/particle neutron" in lines


def test_command_order(tmp_path):
    lines = _write(load_simulation(EXAMPLE), tmp_path)
    initialize = lines.index("/run/initialize")

    # Geometry and output come before /run/initialize; source and run after.
    assert lines.index("/sample/shape cylinder") < initialize
    assert lines.index("/detector/add hpge 30 50 0 80 0") < initialize
    assert initialize < lines.index("/source/particle neutron")
    assert initialize < lines.index("/run/beamOn 10000")


def test_output_file_under_results(tmp_path):
    simulation = load_simulation(EXAMPLE)
    lines = _write(simulation, tmp_path)
    expected = simulation.environment.results_directory / "gamma_hits.parquet"
    assert f"/output/file {expected}" in lines


def test_multiple_detectors(tmp_path):
    simulation = load_simulation(EXAMPLE)
    second = simulation.detectors[0].model_copy(deep=True)
    second.name = "hpge_bottom"
    second.position_mm.y_mm = -80
    simulation.detectors = [simulation.detectors[0], second]
    lines = _write(simulation, tmp_path)

    add_lines = [line for line in lines if line.startswith("/detector/add")]
    assert add_lines == [
        "/detector/add hpge 30 50 0 80 0",
        "/detector/add hpge_bottom 30 50 0 -80 0",
    ]


def test_shielding_block(tmp_path):
    simulation = load_simulation(EXAMPLE)
    simulation.shielding = [
        {"material": "G4_Pb", "thickness_mm": 20, "position_mm": {"x_mm": 0, "y_mm": 40, "z_mm": 0}}
    ]
    lines = _write(simulation, tmp_path)
    assert "/shielding/add G4_Pb 20 0 40 0" in lines


def test_disk_source(tmp_path):
    simulation = load_simulation(EXAMPLE)
    # Set the radius before the shape: validate_assignment re-runs the
    # conditional validator on each assignment, and a disk needs a radius.
    simulation.source.position.radius_mm = 5
    simulation.source.position.shape = "disk"
    lines = _write(simulation, tmp_path)
    assert "/source/shape disk" in lines
    assert "/source/radius 5" in lines


def test_spectrum_energy(tmp_path):
    simulation = load_simulation(EXAMPLE)
    # Set the spectrum file before the type, for the same reason as above.
    simulation.source.energy.spectrum_file = "spectra/cf252.txt"
    simulation.source.energy.type = "spectrum"
    lines = _write(simulation, tmp_path)
    assert "/source/energyType spectrum" in lines
    assert "/source/spectrumFile spectra/cf252.txt" in lines
    assert not any(line.startswith("/source/energy ") for line in lines)


def test_periodic_timing(tmp_path):
    simulation = load_simulation(EXAMPLE)
    # Set the pulse fields before the mode: periodic needs both, and
    # validate_assignment re-runs the validator on each assignment.
    simulation.source.timing.pulse_width_ns = 5
    simulation.source.timing.pulse_period_ns = 1000
    simulation.source.timing.mode = "periodic"
    lines = _write(simulation, tmp_path)
    assert "/source/timing periodic" in lines
    assert "/source/pulseWidth 5" in lines
    assert "/source/pulsePeriod 1000" in lines


# --- Thread count from the CPU-percent cap ---


@pytest.mark.parametrize(
    "cores, percent, expected",
    [
        (16, 80, 12),   # 16 * 80 // 100 = 12
        (8, 80, 6),     # 8 * 80 // 100 = 6
        (16, 100, 16),  # the whole machine
        (16, 1, 1),     # floors at 1, never 0
        (1, 50, 1),     # a single-core machine still gets one thread
        (10, 90, 9),
    ],
)
def test_thread_count_formula(monkeypatch, cores, percent, expected):
    # Fix the core count so the test is independent of the machine it runs on.
    monkeypatch.setattr(macro_module.os, "cpu_count", lambda: cores)
    assert _thread_count(percent) == expected


def test_thread_count_falls_back_to_one_when_cores_unknown(monkeypatch):
    monkeypatch.setattr(macro_module.os, "cpu_count", lambda: None)
    assert _thread_count(80) == 1


def test_macro_sets_thread_count_before_initialize(tmp_path, monkeypatch):
    monkeypatch.setattr(macro_module.os, "cpu_count", lambda: 16)
    simulation = load_simulation(EXAMPLE)  # default cpu_percent = 80
    lines = _write(simulation, tmp_path)

    assert "/run/numberOfThreads 12" in lines
    # The thread count must be set before the run is initialized.
    assert lines.index("/run/numberOfThreads 12") < lines.index("/run/initialize")


def test_macro_thread_count_follows_cpu_percent(tmp_path, monkeypatch):
    monkeypatch.setattr(macro_module.os, "cpu_count", lambda: 16)
    simulation = load_simulation(EXAMPLE)
    simulation.runner.cpu_percent = 50
    lines = _write(simulation, tmp_path)

    assert "/run/numberOfThreads 8" in lines


# --- Random seed ---


def test_macro_sets_the_configured_seed(tmp_path):
    simulation = load_simulation(EXAMPLE)
    simulation.run.seed = 12345
    lines = _write(simulation, tmp_path)

    assert "/random/setSeeds 12345 12345" in lines


def test_seed_command_between_initialize_and_beamon(tmp_path):
    simulation = load_simulation(EXAMPLE)
    lines = _write(simulation, tmp_path)

    # The seed must be set after the run is initialized and before the beam runs.
    seed = next(i for i, line in enumerate(lines) if line.startswith("/random/setSeeds"))
    assert lines.index("/run/initialize") < seed
    assert seed < next(
        i for i, line in enumerate(lines) if line.startswith("/run/beamOn")
    )

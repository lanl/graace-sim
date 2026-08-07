"""Run a simulation end to end from a validated config.

Writes the macro, launches the engine (found on PATH), streams its output to
``logs/run.log``, shows a progress bar, and verifies each detector produced
results. The macro is the only interface to the engine.
"""

import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from loguru import logger

from config.macro import write_macro
from models.simulation import Simulation

# The engine prints `  ... processed N events` every 1000 events
# (sim/src/EventAction.cc); the total is the configured neutron count.
_PROGRESS = re.compile(r"processed\s+(\d+)\s+events")


def _command(config: Simulation, macro_path: Path) -> list[str]:
    """Build the engine command: the resolved binary, its arguments, and the macro."""
    tokens = shlex.split(config.runner.binary)
    if not tokens:
        raise ValueError("`runner.binary` did not resolve to a command.")
    engine = shutil.which(tokens[0])
    if engine is None:
        raise FileNotFoundError(
            f"'{tokens[0]}' is not on PATH; build it with `pixi run build-sim`"
        )
    return [engine, *tokens[1:], str(macro_path)]


def _draw_progress(current: int, total: int) -> None:
    """Draw a single-line progress bar to the terminal."""
    width = 30
    fraction = min(current, total) / total
    filled = int(width * fraction)
    bar = "#" * filled + "-" * (width - filled)
    sys.stderr.write(
        f"\r[{bar}] {int(fraction * 100):3d}% ({min(current, total)}/{total})"
    )
    sys.stderr.flush()
    if current >= total:
        sys.stderr.write("\n")


def _verify_results(config: Simulation) -> None:
    """Check each detector's results directory holds at least one Parquet file."""
    results = config.environment.results_directory
    missing = [
        detector.name
        for detector in config.detectors
        if not list((results / detector.name).glob("*.parquet"))
    ]
    if missing:
        raise FileNotFoundError(
            f"engine finished but no results were written for: {', '.join(missing)}"
        )


def run_simulation(config: Simulation) -> Path:
    """Run ``config`` end to end and return its run directory."""
    macro_path = write_macro(config)
    command = _command(config, macro_path)

    log_directory = config.environment.log_directory
    log_directory.mkdir(parents=True, exist_ok=True)
    log_file = log_directory / "run.log"

    total = config.run.neutrons if config.runner.show_progress else None
    logger.info("Running engine: {}", shlex.join(command))

    with log_file.open("w", encoding="utf-8") as log, subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    ) as process:
        for line in process.stdout:
            log.write(line)
            if total:
                match = _PROGRESS.search(line)
                if match:
                    _draw_progress(int(match.group(1)), total)
        return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(f"engine exited with code {return_code}; see {log_file}")

    if config.runner.verify_output:
        _verify_results(config)

    logger.info("Run complete: {}", config.environment.run_directory)
    return config.environment.run_directory

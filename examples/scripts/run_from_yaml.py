"""Load a simulation config and run it.

    python examples/scripts/run_from_yaml.py <config.yaml>

Run it inside the pixi environment, which puts both Python and the `graace-sim`
engine on PATH. Writes the macro, runs the engine, and lands the macro,
`results/`, and `logs/run.log` together under `data/<run_id>_<sub_run>/`.
"""

import argparse
import sys
from pathlib import Path

# The package lives under src/, which is not installed, so add it to the path.
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from config.yaml_io import load_simulation  # noqa: E402
from runner.run_simulation import run_simulation  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load a simulation config and run it.")
    parser.add_argument("config", type=Path, help="Path to the simulation config YAML file.")
    args = parser.parse_args()
    run_simulation(load_simulation(args.config))

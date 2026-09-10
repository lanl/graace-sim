"""Load a simulation config and run it.

    python examples/scripts/run_from_yaml.py <config.yaml>

Run it inside the pixi environment, which puts both Python and the `graace-sim`
engine on PATH. Writes the macro, runs the engine, and lands the macro,
`results/`, and `logs/run.log` together under `data/<run_id>_<sub_run>/`.
"""

import argparse
from pathlib import Path

from graace_sim.config.yaml_io import load_simulation
from graace_sim.runner.run_simulation import run_simulation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load a simulation config and run it.")
    parser.add_argument("config", type=Path, help="Path to the simulation config YAML file.")
    args = parser.parse_args()
    run_simulation(load_simulation(args.config))

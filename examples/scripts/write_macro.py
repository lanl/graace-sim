"""Load a YAML config and write its GEANT4 macro.

Run it with pixi, optionally passing the config to write (defaults to the
single-detector example):

    pixi run python examples/scripts/write_macro.py
    pixi run python examples/scripts/write_macro.py examples/yaml_files/two_detectors.yaml
"""

import argparse
from pathlib import Path

from graace_sim.config.macro import write_macro
from graace_sim.config.yaml_io import load_simulation

default_config = Path(__file__).parents[2] / "examples" / "yaml_files" / "example.yaml"

parser = argparse.ArgumentParser(description="Load a YAML config and write its GEANT4 macro.")
parser.add_argument(
    "config",
    type=Path,
    nargs="?",
    default=default_config,
    help="Path to the simulation config YAML file (defaults to the single-detector example).",
)
args = parser.parse_args()

simulation = load_simulation(args.config)
macro_path = write_macro(simulation)

print(f"wrote macro: {macro_path}")
print(macro_path.read_text())

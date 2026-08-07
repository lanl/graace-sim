"""Load a YAML config and write its GEANT4 macro.

Run it with pixi, optionally passing the config to write (defaults to the
single-detector example):

    pixi run python examples/scripts/write_macro.py
    pixi run python examples/scripts/write_macro.py examples/yaml_files/two_detectors.yaml
"""

import sys
from pathlib import Path

# The package lives under src/, which is not installed, so add it to the path.
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))

from config.macro import write_macro
from config.yaml_io import load_simulation

# The config path is the first argument; fall back to the example config.
default_config = ROOT / "examples" / "yaml_files" / "example.yaml"
config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_config

simulation = load_simulation(config_path)
macro_path = write_macro(simulation)

print(f"wrote macro: {macro_path}")
print(macro_path.read_text())

"""Load the example YAML config and print a few values from it.

Run it with pixi:

    pixi run python examples/scripts/load_yaml.py
"""

import sys
from pathlib import Path

# The package lives under src/, which is not installed, so add it to the path.
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))

from config.yaml_io import load_simulation

simulation = load_simulation(ROOT / "examples" / "yaml_files" / "example.yaml")

print(f"source:         {simulation.source.energy.mono_mev} MeV {simulation.source.particle}")
print(f"sample:         {simulation.sample.composition.elements[0].symbol} {simulation.sample.shape}")
print(f"detectors:      {[d.type for d in simulation.detectors]}")
print(f"neutrons:       {simulation.run.neutrons}")
print(f"run directory:  {simulation.paths.run_directory}")
print(f"log directory:  {simulation.paths.log_directory}")
print(f"results dir:    {simulation.paths.results_directory}")
print(f"macro file:     {simulation.paths.macro_file}")

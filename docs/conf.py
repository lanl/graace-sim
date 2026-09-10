"""Sphinx configuration for the GRAACE-SIM documentation."""

from pathlib import Path
import sys

# The Python package uses a src layout and is not installed by the docs build.
# Add the repository's src directory so autodoc imports the real package.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

project = "GRAACE-SIM"
copyright = "2026, Triad National Security, LLC"
author = "Triad National Security, LLC"

extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.autodoc_pydantic",
]

# Architecture pages use Mermaid fenced blocks for diagrams.
myst_fence_as_directive = ["mermaid"]
myst_heading_anchors = 3

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

# Keep the generated model pages focused on fields and descriptions.
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_field_list_validators = False

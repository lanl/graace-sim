"""Sphinx configuration for the GRAACE-SIM documentation."""

import os
import sys

# The Python control layer imports its own packages by bare name (e.g.
# `from models.simulation import Simulation`), relying on `src` being on the
# import path. Put it there so autodoc can import the modules.
sys.path.insert(0, os.path.abspath("../src"))

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

# The architecture pages write diagrams as ```mermaid fenced code blocks; hand
# those to the mermaid directive instead of rendering them as literal code.
myst_fence_as_directive = ["mermaid"]

# Give headings anchors so the pages' in-page links (e.g. [Naming](#naming-...))
# resolve.
myst_heading_anchors = 3

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

# Pydantic models: show the fields and validators, drop the noisier summaries.
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_field_list_validators = False

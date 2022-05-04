import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "XDMFWrite_h5py"
copyright = "2021, Tom de Geus"
author = "Tom de Geus"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"

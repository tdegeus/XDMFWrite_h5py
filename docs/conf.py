import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "XDMFWrite_h5py"
copyright = "2021, Tom de Geus"
author = "Tom de Geus"

autodoc_type_aliases = {
    "Iterable": "Iterable",
    "ArrayLike": "ArrayLike",
    "DTypeLike": "DTypeLike",
}

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
]

html_theme = "furo"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

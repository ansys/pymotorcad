"""Sphinx documentation configuration file."""
from datetime import datetime

from ansys_sphinx_theme import ansys_favicon, pyansys_logo_black
from sphinx_gallery.sorting import FileNameSortKey

# Project information
project = "ansys.motorcad.core"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = "0.1.dev1"

# Select desired logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "pymotorcad-core"

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/pyansys/pymotorcad",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/pyansys/pymotorcad/discussions",
            "icon": "fa fa-comment fa-fw",
        },
    ],
}

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    # "sphinx_gallery.gen_gallery",
]

# sphinx_gallery_conf = {
#     # convert rst to md for ipynb
#     "pypandoc": True,
#     # path to your examples scripts
#     "examples_dirs": ["../../examples/"],
#     # path where to save gallery generated examples
#     "gallery_dirs": ["examples/gallery_examples"],
#     # Pattern to search for example files
#     "filename_pattern": r"\.py",
#     # Remove the "Download all examples" button from the top level gallery
#     "download_all_examples": False,
#     # Sort gallery example by file name instead of number of lines (default)
#     "within_subsection_order": FileNameSortKey,
#     # directory where function granular galleries are stored
#     "backreferences_dir": None,
#     # Modules for which function level galleries are created.  In
#     "doc_module": "ansys-motorcad-core",
#     "image_scrapers": "matplotlib",
#     "ignore_pattern": "flycheck*",
# }

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}


# static path
html_static_path = ["_static"]

html_css_files = [
    "custom.css",
]

html_favicon = ansys_favicon

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

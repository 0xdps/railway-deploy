from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../src"))

project = "railway-deploy"
author = "railway-deploy contributors"
copyright = f"{datetime.now():%Y}, {author}"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Theme selection: override with DOCS_THEME env var.
# Supported values: furo, pydata_sphinx_theme, sphinx_book_theme, sphinx_rtd_theme
_theme_options = {
    "furo": {
        "light_css_variables": {
            "color-brand-primary": "#0ea5e9",
            "color-brand-content": "#0284c7",
        }
    },
    "pydata_sphinx_theme": {
        "logo": {
            "text": "railway-deploy",
        },
        "navigation_depth": 2,
        "show_toc_level": 2,
    },
    "sphinx_book_theme": {
        "repository_url": "https://github.com/0xdps/railway-deploy",
        "use_repository_button": True,
        "show_toc_level": 2,
    },
    "sphinx_rtd_theme": {
        "navigation_depth": 4,
        "collapse_navigation": False,
    },
}

html_theme = os.getenv("DOCS_THEME", "furo")
if html_theme not in _theme_options:
    html_theme = "furo"
html_theme_options = _theme_options[html_theme]

html_static_path = ["_static"]
html_logo = "_static/railway-deploy-icon.svg"
html_favicon = "_static/railway-deploy-icon.svg"

# Disable sidebar only for pydata_sphinx_theme
if html_theme == "pydata_sphinx_theme":
    html_sidebars = {"**": []}

autodoc_member_order = "bysource"

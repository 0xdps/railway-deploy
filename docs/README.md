# Documentation

This directory contains the Sphinx documentation for railway-deploy, built for [Read the Docs](https://readthedocs.org/).

## Building Locally

### Prerequisites
- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`

### Build Commands

**Build with default theme (furo):**
```bash
python -m sphinx -b html docs docs/_build/html
```

**Build with a specific theme:**
Use the `DOCS_THEME` environment variable to specify which theme to build:

```bash
# Using pydata_sphinx_theme
DOCS_THEME=pydata_sphinx_theme python -m sphinx -b html docs docs/_build/html

# Using sphinx_book_theme
DOCS_THEME=sphinx_book_theme python -m sphinx -b html docs docs/_build/html

# Using sphinx_rtd_theme
DOCS_THEME=sphinx_rtd_theme python -m sphinx -b html docs docs/_build/html
```

**Live reload during development:**
```bash
# Watch for changes and auto-rebuild (default theme)
sphinx-autobuild docs docs/_build/html

# Watch for changes with a specific theme
DOCS_THEME=sphinx_book_theme sphinx-autobuild docs docs/_build/html
```

## Available Themes

The documentation supports multiple Sphinx themes:

| Theme | Use Case | Features |
|-------|----------|----------|
| **furo** (default) | Minimal, elegant | Clean design, responsive, lightweight |
| **pydata_sphinx_theme** | Data science projects | Modern, product-focused, no sidebar |
| **sphinx_book_theme** | Narrative docs | Book-like layout, great for tutorials |
| **sphinx_rtd_theme** | Classic ReadTheDocs | Familiar RTD style, sidebar navigation |

### Specifying a Theme

Provide the theme name via the `DOCS_THEME` environment variable before the build command:

```bash
# Single command
DOCS_THEME=sphinx_book_theme python -m sphinx -b html docs docs/_build/html

# Or set it for the session
export DOCS_THEME=sphinx_book_theme
python -m sphinx -b html docs docs/_build/html
```

The theme name must match one of the available themes listed above.

## Adding a New Theme

To add a new Sphinx theme:

1. **Install the theme package:**
   ```bash
   pip install sphinx-theme-name
   ```

2. **Add to docs/requirements.txt:**
   ```
   sphinx-theme-name>=version
   ```

3. **Update docs/conf.py:**
   - Import the theme configuration in the `_theme_options` dict:
     ```python
     _theme_options = {
         "existing_theme": {...},
         "new_theme_name": {
             "option_key": "option_value",
             # Add theme-specific options here
         },
     }
     ```

4. **Test the theme:**
   ```bash
   DOCS_THEME=new_theme_name python -m sphinx -b html docs docs/_build/html
   ```

5. **Update this README** with the new theme details.

## Theme-Specific Notes

- **pydata_sphinx_theme**: Sidebar is disabled for a cleaner, product-focused look
- **sphinx_book_theme**: Best for sequential, narrative documentation
- **sphinx_rtd_theme**: Standard choice for API documentation with extensive sidebar navigation

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration, theme switcher
├── requirements.txt     # Python dependencies
├── index.rst            # Documentation home
├── purpose.rst          # Project purpose and scope
├── use-cases.rst        # Real-world use cases
├── installation.rst     # Installation guide
├── usage.rst            # Usage and theme preview
├── configuration.rst    # Configuration details
├── workflow.rst         # Deployment workflow
├── troubleshooting.rst  # Common issues and fixes
├── api.rst              # API reference
├── publishing.rst       # Publishing guide
└── project/             # Open-source governance files
    ├── CHANGELOG.md
    ├── CODE_OF_CONDUCT.md
    ├── CONTRIBUTING.md
    └── SECURITY.md
```

## Useful Links

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Read the Docs](https://readthedocs.org/)
- [Available Sphinx Themes](https://sphinx-themes.readthedocs.io/)

Publishing
==========

Publish to PyPI
---------------

.. code-block:: bash

   python -m pip install -U build twine
   python -m build
   python -m twine check dist/*
   python -m twine upload dist/*

Read the Docs
-------------

This repository is configured with ``.readthedocs.yaml`` using Sphinx.

Steps:

1. Import repository in Read the Docs.
2. Keep default config file path (``.readthedocs.yaml``).
3. Build docs from default branch.

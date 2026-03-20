Usage
=====

This page focuses on day-to-day operator commands.

Authentication
--------------

Export your Railway token:

.. code-block:: bash

   export RAILWAY_TOKEN=<token>

Deploy command
--------------

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/basic.deploy.yml

Production deploy example
-------------------------

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env production --config examples/configs/basic.deploy.yml --env-file .env.production

Options
-------

- ``--service <name>`` deploy only one service from config
- ``--skip-infra`` skip infra creation/provisioning
- ``--env-file <path>`` custom env file path
- ``--no-deploy`` apply config and vars without triggering a deploy action

High-value command combinations
-------------------------------

Deploy one service only:

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/monorepo.deploy.yml --service gateway --skip-infra

Sync variables/config without deploy trigger:

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/monorepo.deploy.yml --no-deploy

Use custom env file path:

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/basic.deploy.yml --env-file examples/env/.env.staging.example

Backward compatibility
----------------------

You can still use:

.. code-block:: bash

   python railway.py --project <ID> --env staging --config examples/configs/basic.deploy.yml

Examples
--------

See the repository examples folder for complete config and env samples:

- ``examples/configs/basic.deploy.yml``
- ``examples/configs/monorepo.deploy.yml``
- ``examples/configs/dashboards.deploy.yml``
- ``examples/env/.env.staging.example``
- ``examples/env/.env.dashboards.staging.example``

Theme options for docs preview
------------------------------

You can switch documentation themes locally by setting ``DOCS_THEME``.

Available options:

- ``furo``
- ``pydata_sphinx_theme``
- ``sphinx_book_theme``
- ``sphinx_rtd_theme``

Examples:

.. code-block:: bash

   DOCS_THEME=pydata_sphinx_theme sphinx-autobuild docs docs/_build/html

.. code-block:: bash

   DOCS_THEME=sphinx_book_theme python -m sphinx -b html docs docs/_build/html

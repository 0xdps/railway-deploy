Usage
=====

Authentication
--------------

Export your Railway token:

.. code-block:: bash

   export RAILWAY_TOKEN=<token>

Deploy command
--------------

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/basic.deploy.yml

Options
-------

- ``--service <name>`` deploy only one service from config
- ``--skip-infra`` skip infra creation/provisioning
- ``--env-file <path>`` custom env file path
- ``--no-deploy`` apply config and vars without triggering a deploy action

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

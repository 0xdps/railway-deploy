Deployment Workflow
===================

End-to-end flow
---------------

This is the runtime workflow used by the CLI:

1. Resolve auth token

- Reads ``RAILWAY_TOKEN`` first.
- Falls back to ``~/.railway/config.json`` token.

2. Resolve environment ID

- Maps ``--env`` name to Railway environment ID.

3. Infra phase (optional)

- For each ``infra`` item, checks if service exists in environment.
- If missing, deploys template (e.g. Postgres/Redis) and waits.

4. Service phase

- Creates service from GitHub source.
- Applies Dockerfile/build/start settings.
- Upserts variables (static + env + references).

5. Deploy trigger phase

- Calls deploy/redeploy depending on state and flags.

Command patterns
----------------

Full deploy:

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/basic.deploy.yml

Service-only deploy:

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/monorepo.deploy.yml --service gateway --skip-infra

Variables/config only (no deploy trigger):

.. code-block:: bash

   railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/monorepo.deploy.yml --no-deploy

Configuration
=============

Use ``examples/configs/deploy.example.yml`` as your base template.

Top-level keys
--------------

``project``
  Metadata for naming and workspace linkage.

  - ``name``: human-friendly project label for logs
  - ``prefix``: service naming prefix used in infra/service names
  - ``workspace_id``: required for template-based infra provisioning

``infra``
  Infrastructure services provisioned first (postgres, redis).

  Common keys per infra item:

  - ``name`` / ``type``: ``postgres`` or ``redis``
  - ``image``: optional image override
  - ``wait_seconds``: optional startup wait after provisioning

``services``
  Application services to deploy in order.

  Common keys per service item:

  - ``name``: logical name used by ``--service``
  - ``railway_name``: target Railway service name prefix
  - ``repo`` and ``branch``: GitHub source
  - ``dockerfile`` / ``build_command`` / ``start_command``: instance settings
  - ``vars`` block: static, common, and reference variables

``secrets``, ``required_vars``, ``soft_vars``, ``env_template``
  Optional governance keys for your own workflows.

Service var blocks
------------------

Each service supports:

- ``vars.static``: hardcoded values
- ``vars.common``: keys pulled from env file
- ``vars.references``: Railway references (``${{service.KEY}}``)

Minimal complete service example
--------------------------------

.. code-block:: yaml

   services:
     - name: api
       railway_name: example-api
       repo: your-org/your-repo
       branch: main
       dockerfile: Dockerfile
       vars:
         static:
           NODE_ENV: production
         common:
           - APP_SECRET
           - API_PUBLIC_URL
         references:
           DATABASE_URL: example-postgres.DATABASE_URL

Validation tips
---------------

- Keep service ``name`` unique in a config.
- Ensure every ``vars.common`` key exists in your env file.
- Keep ``workspace_id`` set for infra-enabled configs.

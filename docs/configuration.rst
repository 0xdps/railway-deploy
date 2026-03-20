Configuration
=============

Use ``examples/configs/deploy.example.yml`` as your base template.

Top-level keys
--------------

``project``
  Metadata for naming and workspace linkage.

``infra``
  Infrastructure services provisioned first (postgres, redis).

``services``
  Application services to deploy in order.

``secrets``, ``required_vars``, ``soft_vars``, ``env_template``
  Optional governance keys for your own workflows.

Service var blocks
------------------

Each service supports:

- ``vars.static``: hardcoded values
- ``vars.common``: keys pulled from env file
- ``vars.references``: Railway references (``${{service.KEY}}``)

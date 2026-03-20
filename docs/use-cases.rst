Use Cases
=========

Common adoption patterns
------------------------

1. Standard staging deploys

- Team keeps ``examples/configs/basic.deploy.yml``-style config in repo.
- CI runs one command on merge to staging branch.
- Result: same behavior every deploy, less operator drift.

2. Multi-service monorepo rollout

- One config describes ``core``, ``gateway``, and ``workers`` services.
- Shared references (e.g. Postgres/Redis URLs) stay consistent.
- Result: fewer mismatch errors across services.

3. New environment bootstrap

- Provision infra + services for preview/staging environments.
- Reuse same template with different env files.
- Result: predictable bootstrapping and simpler onboarding.

4. Controlled service-only deploys

- Use ``--service <name>`` to deploy one service after a targeted change.
- Use ``--skip-infra`` when infra already exists.
- Result: faster deploy cycles with reduced blast radius.

5. GitHub auto-deploy workflows

- Keep Railway connected to GitHub for auto builds.
- Run with ``--no-deploy`` when only config/vars need updates.
- Result: avoid accidental double-build triggers.

When this tool is a strong fit
------------------------------

- You have more than one Railway service.
- You want deployment config in version control.
- You need predictable environment setup across teams.

When a simpler option may be enough
-----------------------------------

- You operate a single service with infrequent changes.
- Manual dashboard actions are acceptable for your team.

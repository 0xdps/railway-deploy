Purpose and Scope
=================

What this project solves
------------------------

``railway-deploy`` exists to make Railway deployments repeatable and auditable.

Many teams start by deploying through the Railway dashboard. That works well for
initial setup, but over time teams usually need:

- consistent deployment behavior across staging/production
- a reproducible config checked into version control
- fewer manual clicks and less copy-paste between services
- a safe way to re-run infra + app deploys during incidents

This tool provides those benefits through config-as-code.

Why this approach
-----------------

The CLI follows a fixed lifecycle:

1. Provision infra (Postgres/Redis templates)
2. Create service(s) from GitHub source
3. Apply service instance build/start settings
4. Upsert variables for each service
5. Trigger deployment

Because each step is explicit, operators can reason about failures faster and
rerun with confidence.

What is intentionally in scope
------------------------------

- Railway project/environment deployments driven by YAML
- Multi-service app setups (single repo or monorepo)
- Infra + app orchestration in one command
- CI-friendly command invocation

What is intentionally out of scope
----------------------------------

- Full secrets lifecycle management across cloud providers
- Runtime health orchestration beyond Railway deployment APIs
- Replacing Railway CLI for every feature

For these, combine ``railway-deploy`` with your existing platform tooling.

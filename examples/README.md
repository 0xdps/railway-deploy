# Examples

This folder contains copy-ready examples for common deployment setups.

## Config examples

- configs/basic.deploy.yml: single app service + postgres + redis
- configs/monorepo.deploy.yml: core + gateway monorepo pattern
- configs/dashboards.deploy.yml: static dashboards service with gateway proxy vars
- configs/deploy.example.yml: generic template for new projects
- configs/nube-auth.deploy.yml: real-world multi-service setup
- configs/nube-auth-dashboards.deploy.yml: real-world dashboards setup

## Env examples

- env/.env.staging.example: generic staging env variables
- env/.env.dashboards.staging.example: dashboard-specific env variables

## Postman

- postman/railway-deploy.postman_collection.json: Railway GraphQL collection

## Usage

Run with any example config:

```bash
railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/basic.deploy.yml
```

Or with compatibility script:

```bash
python railway.py --project <PROJECT_ID> --env staging --config examples/configs/basic.deploy.yml
```

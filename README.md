# railway-deploy

Declarative Railway deployment CLI for application services and managed infrastructure.

`railway-deploy` reads a YAML config file and executes a predictable deployment flow:
1. Provision infra services from Railway templates (Postgres, Redis)
2. Create application services from GitHub source
3. Apply build/start config and environment variables
4. Trigger deployment

## Purpose

`railway-deploy` is built for teams that want the speed of Railway with the
repeatability of config-as-code.

It helps answer common operational questions:

- Why did this environment differ from last week?
- Which variables/config were applied to this service?
- Can we recreate staging quickly and consistently?

By storing deploy intent in versioned YAML, teams reduce manual drift and make
deploy behavior easier to review.

## Why this project

Railway's dashboard is great for manual setup, but repeated environment provisioning and multi-service rollout can become error-prone. This tool provides an auditable, repeatable deployment process with config-as-code.

## Features

- Railway GraphQL public API integration for app services
- Railway internal template flow for infra parity with dashboard behavior
- Multi-service deploy from a single YAML config
- `.env.<environment>` support for variable injection
- Safe output masking for sensitive keys
- Single-service deploy mode for targeted updates
- Compatibility script (`railway.py`) plus installable CLI command (`railway-deploy`)

## Who this is for

- Teams running multiple Railway services
- Projects with staging + production environments
- Monorepos deploying multiple services in a controlled order
- CI/CD pipelines that need deterministic deploy commands

## Typical use-cases

- Bootstrap a fresh environment with infra + apps in one run
- Deploy a single service after a targeted code change (`--service`)
- Update config/variables without triggering build (`--no-deploy`)
- Keep deployment definitions in pull requests and code review

## Installation

### From source

```bash
git clone https://github.com/0xdps/railway-deploy.git
cd railway-deploy
python -m pip install -U pip
python -m pip install -e .
```

### Runtime dependencies only

```bash
python -m pip install -r requirements.txt
```

## Quick start

1. Create a deploy config file (start from [examples/configs/deploy.example.yml](examples/configs/deploy.example.yml)).
2. Export your Railway token:

```bash
export RAILWAY_TOKEN=<your_token>
```

3. Run deployment:

```bash
railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/basic.deploy.yml
```

Monorepo example:

```bash
railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/monorepo.deploy.yml
```

Service-only rollout example:

```bash
railway-deploy --project <PROJECT_ID> --env staging --config examples/configs/monorepo.deploy.yml --service gateway --skip-infra
```

## Example files

Ready-to-copy examples are available in [examples](examples):

- [examples/configs/basic.deploy.yml](examples/configs/basic.deploy.yml)
- [examples/configs/monorepo.deploy.yml](examples/configs/monorepo.deploy.yml)
- [examples/configs/dashboards.deploy.yml](examples/configs/dashboards.deploy.yml)
- [examples/configs/deploy.example.yml](examples/configs/deploy.example.yml)
- [examples/configs/nube-auth.deploy.yml](examples/configs/nube-auth.deploy.yml)
- [examples/configs/nube-auth-dashboards.deploy.yml](examples/configs/nube-auth-dashboards.deploy.yml)
- [examples/postman/railway-deploy.postman_collection.json](examples/postman/railway-deploy.postman_collection.json)
- [examples/env/.env.staging.example](examples/env/.env.staging.example)
- [examples/env/.env.dashboards.staging.example](examples/env/.env.dashboards.staging.example)

## CLI usage

```text
railway-deploy --project <ID> --env <staging|production> --config <config.yml> [options]

Options:
  --service <name>     Deploy only one service from config
  --skip-infra         Skip infra provisioning block
  --env-file <path>    Use specific env file (default: .env.<env>)
  --no-deploy          Configure service but skip deploy trigger
```

Backward compatible launcher:

```bash
python railway.py --project <ID> --env staging --config examples/configs/basic.deploy.yml
```

## Project layout

```text
src/railway_deploy/
  cli.py          # argparse CLI and orchestration wiring
  clients.py      # GraphQL clients (public/internal)
  config.py       # config loader
  deploy.py       # deploy orchestration helpers
  output.py       # console output and masking
  templates.py    # infra template payload builders
railway.py        # compatibility entrypoint
docs/             # Sphinx docs for Read the Docs
examples/         # ready-to-copy configs, env files, and Postman collection
```

## Configuration format

Use [examples/configs/deploy.example.yml](examples/configs/deploy.example.yml) as the base template.

Top-level keys:
- `project`: project metadata (`name`, `prefix`, `workspace_id`)
- `infra`: infra services (e.g. postgres, redis)
- `services`: app services and runtime/build config
- `secrets`, `required_vars`, `soft_vars`, `env_template`: optional governance fields for your own process

## Publish to PyPI

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

## Documentation

- Source docs: [docs/](docs/)
- Read the Docs config: [.readthedocs.yaml](.readthedocs.yaml)
- Purpose and scope: [docs/purpose.rst](docs/purpose.rst)
- Operational use-cases: [docs/use-cases.rst](docs/use-cases.rst)
- Deployment lifecycle: [docs/workflow.rst](docs/workflow.rst)
- Troubleshooting: [docs/troubleshooting.rst](docs/troubleshooting.rst)

## Security

Never commit real secrets. `.env.*` is ignored by default.

Report vulnerabilities privately. See [docs/project/SECURITY.md](docs/project/SECURITY.md).

## Contributing

See [docs/project/CONTRIBUTING.md](docs/project/CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

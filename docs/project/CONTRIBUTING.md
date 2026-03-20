# Contributing

Thanks for helping improve `railway-deploy`.

## Development setup

```bash
git clone https://github.com/0xdps/railway-deploy.git
cd railway-deploy
python -m pip install -U pip
python -m pip install -e .
```

## Coding guidelines

- Keep changes focused and minimal.
- Preserve backward compatibility for `railway.py` entrypoint unless a breaking change is planned.
- Avoid logging secrets.
- Add/update docs when behavior changes.

## Suggested checks

```bash
python -m compileall src railway.py
```

## Pull requests

- Explain the problem and the change.
- Include reproduction steps and verification commands.
- Update `CHANGELOG.md` for user-facing changes.

## Reporting issues

Please include:
- command used
- sanitized config snippet
- error output
- Python version and OS

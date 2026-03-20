"""Console output utilities."""

from __future__ import annotations

import re
import sys


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text


def step(msg: str) -> None:
    print(f"\n{_c('36;1', '▸')} {_c('1', msg)}")


def ok(msg: str) -> None:
    print(f"  {_c('32', '✓')} {msg}")


def info(msg: str) -> None:
    print(f"  {_c('2', '→')} {msg}")


def warn(msg: str) -> None:
    print(f"  {_c('33', '⚠')} {msg}")


def die(msg: str) -> None:
    print(f"\n{_c('31;1', 'ERROR')}: {msg}\n", file=sys.stderr)
    raise SystemExit(1)


SENSITIVE = re.compile(r"(SECRET|KEY|TOKEN|PASSWORD|PASS|CREDENTIAL|PRIVATE)", re.IGNORECASE)


def mask(k: str, v: str) -> str:
    return "[redacted]" if SENSITIVE.search(k) else v

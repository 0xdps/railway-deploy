#!/usr/bin/env python3
"""Backward-compatible script entrypoint.

Prefer using the installed CLI command:
  railway-deploy --project <ID> --env staging --config examples/configs/basic.deploy.yml
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

if __name__ == "__main__":
    from railway_deploy.cli import main

    main()

"""Configuration parsing for deploy YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml


class Config:
    """Thin wrapper around the YAML deploy config."""

    def __init__(self, raw: dict) -> None:
        proj = raw.get("project", {})
        self.name: str = proj.get("name", "app")
        self.prefix: str = proj.get("prefix", "app")
        self.workspace_id: str = proj.get("workspace_id", "")
        self.infra: list[dict] = raw.get("infra", [])
        self.services: list[dict] = raw.get("services", [])
        self.secrets: list[dict] = raw.get("secrets", [])
        self.required_vars: list[str] = raw.get("required_vars", [])
        self.soft_vars: list[str] = raw.get("soft_vars", [])

    @classmethod
    def load(cls, path: Path) -> "Config":
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")))

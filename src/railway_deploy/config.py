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

    @staticmethod
    def make_service_name(prefix: str, env: str, name: str, postfix: str = "") -> str:
        """Build a Railway service name following the convention: prefix-env-name[-postfix]."""
        parts = [prefix, env, name]
        if postfix:
            parts.append(postfix)
        return "-".join(parts)

    def build_name_map(self, env: str, postfix: str = "") -> dict[str, str]:
        """Pre-compute Railway service names for all infra and services.

        Explicit ``railway_name`` in the YAML wins; otherwise the naming
        convention ``{prefix}-{env}-{name}[-{postfix}]`` is applied.
        """
        result: dict[str, str] = {}
        for svc in self.services:
            result[svc["name"]] = svc.get("railway_name") or self.make_service_name(
                self.prefix, env, svc["name"], postfix
            )
        for infra in self.infra:
            result[infra["name"]] = infra.get("railway_name") or self.make_service_name(
                self.prefix, env, infra["name"], postfix
            )
        return result

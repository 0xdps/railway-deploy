"""Deploy orchestration helpers."""

from __future__ import annotations

import json
import os
import secrets as _secrets
import time
import uuid
from pathlib import Path

from .clients import InternalClient, PublicClient
from .config import Config
from .output import die, info, mask, ok, step, warn
from .templates import INFRA_TEMPLATES


def build_service_vars(service: dict, env_vars: dict[str, str]) -> dict[str, str]:
    """Build final variable dict from one service config block."""
    result: dict[str, str] = {}
    cfg = service.get("vars", {})

    for key, value in cfg.get("static", {}).items():
        result[key] = str(value)

    for key in cfg.get("common", []):
        if value := env_vars.get(key):
            result[key] = value

    for destination, ref in cfg.get("references", {}).items():
        result[destination] = ref if ref.startswith("${{") else f"${{{{{ref}}}}}"

    return result


def load_env_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        warn(f"Env file not found: {path}  (continuing without it)")
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def generate_secrets(config: "Config", env_vars: dict[str, str]) -> dict[str, str]:
    """Generate cryptographically secure values for any secret that is absent or empty."""
    from .config import Config  # local import avoids circular dep at module level
    generated = []
    for secret in config.secrets:
        key = secret.get("key", "")
        n_bytes = int(secret.get("bytes", 32))
        if key and not env_vars.get(key):
            env_vars[key] = _secrets.token_hex(n_bytes)
            generated.append(f"{key} ({n_bytes} bytes)")
    if generated:
        info(f"Auto-generated secrets: {', '.join(generated)}")
    return env_vars


def check_required_vars(config: "Config", env_vars: dict[str, str]) -> None:
    """Die if any hard-required variable is still missing after secret generation."""
    from .config import Config  # local import avoids circular dep at module level
    missing = [k for k in config.required_vars if not env_vars.get(k)]
    if missing:
        die(f"Missing required variables: {', '.join(missing)}\n  Add them to your env file.")


def check_soft_vars(config: "Config", env_vars: dict[str, str]) -> None:
    """Warn for soft-required variables that are empty (features may be degraded)."""
    from .config import Config  # local import avoids circular dep at module level
    for key in config.soft_vars:
        if not env_vars.get(key):
            warn(f"Optional variable '{key}' is empty — related features may be disabled")


def resolve_token() -> str:
    if token := os.environ.get("RAILWAY_TOKEN", "").strip():
        return token
    cfg = Path.home() / ".railway" / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            if token := (data.get("user") or {}).get("token", "").strip():
                return token
        except Exception:
            pass
    die("No RAILWAY_TOKEN found.\n  export RAILWAY_TOKEN=<your_token>")
    return ""


def deploy_infra(
    cfg: Config,
    infra: dict,
    project_id: str,
    env_id: str,
    public_client: PublicClient,
    internal_client: InternalClient,
) -> None:
    infra_type = (infra.get("type") or infra.get("name", "")).lower()
    template = INFRA_TEMPLATES.get(infra_type)
    if not template:
        warn(f"Unknown infra type '{infra_type}' - skipping")
        return

    template_id, default_image, build_fn, wait_seconds = template
    name = infra.get("railway_name") or f"{cfg.prefix}-{infra_type}"
    image = infra.get("image") or default_image

    step(f"Provisioning {infra_type.capitalize()}")

    service_id = public_client.find_service_id(project_id, name)
    if service_id and public_client.has_env_instance(service_id, env_id):
        ok(f"Already exists -> {name} ({service_id})")
        return

    if not cfg.workspace_id:
        die(
            "Missing 'workspace_id' under 'project:' in your deploy config.\n"
            "  Find it in your Railway dashboard URL: railway.com/workspace/<id>"
        )

    service_uuid = str(uuid.uuid4())
    serialized = build_fn(service_uuid, name, image)

    info(f"Deploying {name} ({image}) with persistent volume...")
    try:
        workflow_id = internal_client.deploy_template(
            project_id, env_id, cfg.workspace_id, template_id, serialized
        )
        ok(f"Template deployed - workflow: {workflow_id.split('/')[-1]}")
        public_client.invalidate()
    except RuntimeError as exc:
        die(f"templateDeployV2 failed: {exc}")

    if wait_seconds:
        info(f"Waiting {wait_seconds}s for {infra_type.capitalize()} to initialise...")
        time.sleep(wait_seconds)


def deploy_service(
    svc: dict,
    project_id: str,
    env_id: str,
    env_vars: dict[str, str],
    public_client: PublicClient,
    no_deploy: bool = False,
) -> str:
    name = svc["railway_name"]
    repo = svc.get("repo", "")
    branch = svc.get("branch", "main")
    dockerfile = svc.get("dockerfile", "")
    build_command = svc.get("build_command", "")
    start_command = svc.get("start_command", "")
    http_endpoint = svc.get("http_endpoint", False)
    health_check = svc.get("health_check", {})
    healthcheck_path = health_check.get("path", "")
    healthcheck_timeout = int(health_check.get("timeout", 0))

    if not repo:
        die(f"Service '{name}' is missing 'repo' in config (e.g. repo: owner/repo-name)")

    step(f"Deploying {name}")

    # Use the exact railway_name — no random suffix — so Railway private networking
    # (e.g. nubeauth-core.railway.internal) resolves correctly between services.
    # If a service with this name already exists, update it in place.
    existing_id = public_client.find_service_id(project_id, name)
    if existing_id and public_client.has_env_instance(existing_id, env_id):
        service_id = existing_id
        info(f"Service '{name}' already exists ({service_id}) — updating in place")
    elif existing_id:
        # Service exists but has no instance in the target environment.
        # Railway only creates ServiceInstances for environments that exist at creation time.
        # serviceConnect (and other per-env mutations) fail with "ServiceInstance not found"
        # when the target env instance is absent.
        # Fix: delete and recreate WITHOUT environmentId so Railway creates instances in ALL environments.
        warn(f"Service '{name}' ({existing_id}) has no instance in target environment — deleting and recreating...")
        public_client.delete_service(existing_id)
        public_client.invalidate()
        info(f"Creating service '{name}' (no source, no environmentId — instances in all envs)")
        service_id = public_client.create_service(project_id, name)
        public_client.invalidate()
        existing_id = None  # treat as brand new for the deploy path below
        ok(f"Service recreated -> {service_id}")
    else:
        info(f"Creating service '{name}' (no source yet — avoids premature deploy)")
        service_id = public_client.create_service(project_id, name)
        public_client.invalidate()
        ok(f"Service created -> {service_id}")

    public_client.update_instance(
        service_id,
        env_id,
        dockerfile_path=dockerfile,
        build_command=build_command,
        start_command=start_command,
        healthcheck_path=healthcheck_path,
        healthcheck_timeout=healthcheck_timeout,
    )
    ok(f"Build config applied (dockerfile={dockerfile or 'none'}, healthcheck={healthcheck_path or 'none'})")

    if http_endpoint:
        try:
            domain = public_client.create_service_domain(service_id, env_id)
            ok(f"Public HTTP endpoint created -> https://{domain}")
        except RuntimeError as exc:
            warn(f"Could not create public endpoint (may already exist): {exc}")

    variables = build_service_vars(svc, env_vars)
    for key, value in variables.items():
        info(f"  {key} = {mask(key, value)}")
    public_client.set_variables(project_id, env_id, service_id, variables)
    ok(f"Variables set ({len(variables)} keys)")

    if no_deploy:
        info(f"Skipping repo connection (--no-deploy flag set) — connect manually: {repo}@{branch}")
    else:
        if existing_id and public_client.has_env_instance(existing_id, env_id):
            # Service already has a repo — just trigger a redeploy with updated vars/config
            info(f"Redeploying existing service {name}...")
            try:
                public_client.redeploy(service_id, env_id)
                ok("Redeploy triggered")
            except RuntimeError as exc:
                warn(f"Redeploy trigger failed (may deploy automatically): {exc}")
        else:
            info(f"Connecting repo {repo}@{branch} — triggers first (and only) deployment...")
            public_client.connect_service(service_id, repo, branch)
            ok("Repo connected — Railway deployment triggered")

    return service_id


def print_project_summary(public_client: PublicClient, project_id: str, env_id: str, deployed_ids: set[str] | None = None) -> None:
    public_client.invalidate()
    print("\n  Services in environment:")
    for service in sorted(public_client.list_services(project_id, env_id), key=lambda item: item["name"]):
        marker = "> " if deployed_ids and service["id"] in deployed_ids else "  "
        print(f"   {marker}{service['name']}  ({service['id']})")

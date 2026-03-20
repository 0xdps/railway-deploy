"""Deploy orchestration helpers."""

from __future__ import annotations

import json
import os
import random
import string
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
) -> None:
    name = svc["railway_name"]
    repo = svc.get("repo", "")
    branch = svc.get("branch", "main")
    dockerfile = svc.get("dockerfile", "")
    build_command = svc.get("build_command", "")
    start_command = svc.get("start_command", "")

    if not repo:
        die(f"Service '{name}' is missing 'repo' in config (e.g. repo: owner/repo-name)")

    step(f"Deploying {name}")

    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    deployed_name = f"{name}-{suffix}"
    info(f"Creating service '{deployed_name}' from {repo}@{branch}")
    service_id = public_client.create_service(project_id, deployed_name, repo, branch)
    public_client.invalidate()
    ok(f"Service created -> {service_id}")
    is_new = True

    public_client.update_instance(
        service_id,
        env_id,
        dockerfile_path=dockerfile,
        build_command=build_command,
        start_command=start_command,
    )
    ok(f"Build config applied (dockerfile={dockerfile or 'none'})")

    variables = build_service_vars(svc, env_vars)
    for key, value in variables.items():
        info(f"  {key} = {mask(key, value)}")
    public_client.set_variables(project_id, env_id, service_id, variables)
    ok(f"Variables set ({len(variables)} keys)")

    if no_deploy and not is_new:
        info("Skipping manual deploy trigger (GitHub auto-deploy will handle it)")
    elif is_new:
        public_client.deploy(service_id, env_id)
        ok("Deployment triggered")
    else:
        public_client.redeploy(service_id, env_id)
        ok("Redeployment triggered")


def print_project_summary(public_client: PublicClient, project_id: str) -> None:
    public_client.invalidate()
    print("\n  Services in project:")
    for service in sorted(public_client.list_services(project_id), key=lambda item: item["name"]):
        print(f"    {service['name']}  ({service['id']})")

"""CLI entrypoint for railway-deploy."""

from __future__ import annotations

import argparse
from pathlib import Path

from .clients import InternalClient, PublicClient
from .config import Config
from .deploy import deploy_infra, deploy_service, load_env_file, print_project_summary, resolve_token
from .output import die, warn


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Railway deployment tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    railway-deploy --project <ID> --env staging --config examples/configs/basic.deploy.yml
    railway-deploy --project <ID> --env staging --config examples/configs/nube-auth.deploy.yml --skip-infra
    railway-deploy --project <ID> --env staging --config examples/configs/nube-auth.deploy.yml --service core
""",
    )
    parser.add_argument("--project", required=True, help="Railway project ID")
    parser.add_argument("--env", required=True, help="Environment name (e.g. staging, production)")
    parser.add_argument("--config", required=True, help="Path to deploy config YAML")
    parser.add_argument("--service", default="all", help="Deploy a single service by name (default: all)")
    parser.add_argument("--skip-infra", action="store_true", help="Skip infra provisioning")
    parser.add_argument("--env-file", help="Path to env file (default: .env.<env>)")
    parser.add_argument(
        "--no-deploy",
        action="store_true",
        help="Set variables and config but skip triggering a build",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        die(f"Config file not found: {config_path}")
    config = Config.load(config_path)

    env_file = Path(args.env_file).resolve() if args.env_file else Path.cwd() / f".env.{args.env}"
    env_vars = load_env_file(env_file)

    token = resolve_token()
    public_client = PublicClient(token)
    internal_client = InternalClient(token)

    env_id = public_client.get_env_id(args.project, args.env)

    print(f"\n  Project   {args.project}")
    print(f"  Env       {args.env} -> {env_id}")
    print(f"  Config    {config_path}")
    print(f"  Env file  {env_file}\n")

    if not args.skip_infra:
        for infra in config.infra:
            deploy_infra(config, infra, args.project, env_id, public_client, internal_client)
    else:
        warn("Skipping infra provisioning (--skip-infra)")

    services = (
        config.services if args.service == "all" else [s for s in config.services if s["name"] == args.service]
    )
    if args.service != "all" and not services:
        valid = ", ".join(service["name"] for service in config.services)
        die(f"Service '{args.service}' not found. Valid names: {valid}")

    for service in services:
        deploy_service(service, args.project, env_id, env_vars, public_client, no_deploy=args.no_deploy)

    print_project_summary(public_client, args.project, env_id)
    print("\n  Done!\n")


if __name__ == "__main__":
    main()

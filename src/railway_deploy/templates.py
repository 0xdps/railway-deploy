"""Infra template builders used with templateDeployV2."""

from __future__ import annotations

from .constants import POSTGRES_TEMPLATE, REDIS_TEMPLATE


def _postgres_config(svc_uuid: str, name: str, image: str) -> dict:
    return {
        "services": {
            svc_uuid: {
                "icon": "https://devicons.railway.app/i/postgresql.svg",
                "name": name,
                "build": {},
                "deploy": {"requiredMountPath": "/var/lib/postgresql/data"},
                "source": {"image": image},
                "variables": {
                    "PGDATA": {
                        "isOptional": False,
                        "defaultValue": "/var/lib/postgresql/data/pgdata",
                    },
                    "PGHOST": {"isOptional": False, "defaultValue": "${{RAILWAY_PRIVATE_DOMAIN}}"},
                    "PGPORT": {"isOptional": False, "defaultValue": "5432"},
                    "PGUSER": {"isOptional": False, "defaultValue": "${{ POSTGRES_USER }}"},
                    "PGDATABASE": {"isOptional": False, "defaultValue": "${{POSTGRES_DB}}"},
                    "PGPASSWORD": {
                        "isOptional": False,
                        "defaultValue": "${{POSTGRES_PASSWORD}}",
                    },
                    "POSTGRES_DB": {"isOptional": False, "defaultValue": "railway"},
                    "POSTGRES_USER": {"isOptional": False, "defaultValue": "postgres"},
                    "POSTGRES_PASSWORD": {
                        "isOptional": False,
                        "defaultValue": '${{ secret(32, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") }}',
                    },
                    "DATABASE_URL": {
                        "isOptional": False,
                        "defaultValue": "postgresql://${{PGUSER}}:${{POSTGRES_PASSWORD}}@${{RAILWAY_PRIVATE_DOMAIN}}:5432/${{PGDATABASE}}",
                    },
                    "DATABASE_PUBLIC_URL": {
                        "defaultValue": "postgresql://${{PGUSER}}:${{POSTGRES_PASSWORD}}@${{RAILWAY_TCP_PROXY_DOMAIN}}:${{RAILWAY_TCP_PROXY_PORT}}/${{PGDATABASE}}",
                    },
                    "RAILWAY_DEPLOYMENT_DRAINING_SECONDS": {
                        "isOptional": False,
                        "defaultValue": "60",
                    },
                },
                "networking": {"tcpProxies": {"5432": {}}, "serviceDomains": {}},
                "volumeMounts": {svc_uuid: {"mountPath": "/var/lib/postgresql/data"}},
            }
        }
    }


def _redis_config(svc_uuid: str, name: str, image: str) -> dict:
    start_cmd = (
        '/bin/sh -c "rm -rf $RAILWAY_VOLUME_MOUNT_PATH/lost+found/ && '
        'exec docker-entrypoint.sh redis-server --requirepass $REDIS_PASSWORD '
        '--save 60 1 --dir $RAILWAY_VOLUME_MOUNT_PATH"'
    )
    return {
        "services": {
            svc_uuid: {
                "icon": "https://cdn.sanity.io/images/sy1jschh/production/0ce0bfdcfbdbf69662b1116671f97c2dd788b655-157x157.svg",
                "name": name,
                "deploy": {"startCommand": start_cmd},
                "source": {"image": image},
                "variables": {
                    "REDISHOST": {"isOptional": False, "defaultValue": "${{RAILWAY_PRIVATE_DOMAIN}}"},
                    "REDISPORT": {"isOptional": False, "defaultValue": "6379"},
                    "REDISUSER": {"isOptional": False, "defaultValue": "default"},
                    "REDIS_PASSWORD": {
                        "isOptional": False,
                        "defaultValue": '${{ secret(32, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") }}',
                    },
                    "REDISPASSWORD": {"isOptional": False, "defaultValue": "${{REDIS_PASSWORD}}"},
                    "REDIS_URL": {
                        "isOptional": False,
                        "description": "Private network connection string",
                        "defaultValue": "redis://${{ REDISUSER }}:${{ REDIS_PASSWORD }}@${{ REDISHOST }}:${{ REDISPORT }}",
                    },
                    "REDIS_PUBLIC_URL": {
                        "defaultValue": "redis://default:${{ REDIS_PASSWORD }}@${{ RAILWAY_TCP_PROXY_DOMAIN }}:${{ RAILWAY_TCP_PROXY_PORT }}",
                    },
                },
                "networking": {"tcpProxies": {"6379": {}}},
                "volumeMounts": {svc_uuid: {"mountPath": "/data"}},
            }
        }
    }


# template_id, default_image, config_builder_fn, post_deploy_wait_seconds
INFRA_TEMPLATES: dict[str, tuple] = {
    "postgres": (
        POSTGRES_TEMPLATE,
        "ghcr.io/railwayapp-templates/postgres-ssl:18",
        _postgres_config,
        15,
    ),
    "redis": (REDIS_TEMPLATE, "redis:8.2.1", _redis_config, 5),
}

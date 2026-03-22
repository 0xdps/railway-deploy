"""Railway API clients (public + internal GraphQL)."""

from __future__ import annotations

from typing import Any

import requests

from .constants import INTERNAL_API, PUBLIC_API
from .output import die


class PublicClient:
    """Client for https://backboard.railway.app/graphql/v2."""

    def __init__(self, token: str) -> None:
        self._s = requests.Session()
        self._s.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )
        self._env_cache: dict[str, str] = {}
        self._svc_cache: list[dict] | None = None

    def _gql(self, query: str, variables: dict | None = None) -> dict:
        body: dict[str, Any] = {"query": query}
        if variables:
            body["variables"] = variables
        resp = self._s.post(PUBLIC_API, json=body, timeout=30)
        if not resp.ok:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise RuntimeError(f"HTTP {resp.status_code}: {detail}")
        data = resp.json()
        if errors := data.get("errors"):
            raise RuntimeError(errors[0]["message"])
        return data["data"]

    def get_env_id(self, project_id: str, env_name: str) -> str:
        cache_key = f"{project_id}:{env_name}"
        if cache_key not in self._env_cache:
            data = self._gql(
                "query($id:String!){project(id:$id){environments{edges{node{id name}}}}}",
                {"id": project_id},
            )
            for edge in data["project"]["environments"]["edges"]:
                node = edge["node"]
                if node["name"] == env_name:
                    self._env_cache[cache_key] = node["id"]
                    break
        if cache_key not in self._env_cache:
            die(f"Environment '{env_name}' not found in project '{project_id}'")
        return self._env_cache[cache_key]

    def list_services(self, project_id: str, env_id: str | None = None) -> list[dict]:
        if self._svc_cache is None:
            data = self._gql(
                "query($id:String!){project(id:$id){services{edges{node{id name serviceInstances{edges{node{environmentId}}}}}}}}" ,
                {"id": project_id},
            )
            self._svc_cache = [
                {"id": edge["node"]["id"], "name": edge["node"]["name"], "env_ids": [
                    inst["node"]["environmentId"]
                    for inst in edge["node"]["serviceInstances"]["edges"]
                ]}
                for edge in data["project"]["services"]["edges"]
            ]
        if env_id is not None:
            return [s for s in self._svc_cache if env_id in s["env_ids"]]
        return self._svc_cache

    def find_service_id(self, project_id: str, name: str) -> str | None:
        needle = name.lower()
        for service in self.list_services(project_id):
            if service["name"].lower() == needle:
                return service["id"]
        return None

    def invalidate(self) -> None:
        self._svc_cache = None

    def has_env_instance(self, service_id: str, env_id: str) -> bool:
        try:
            data = self._gql(
                "query($id:String!){service(id:$id){serviceInstances{edges{node{environmentId}}}}}",
                {"id": service_id},
            )
            return any(
                edge["node"]["environmentId"] == env_id
                for edge in data["service"]["serviceInstances"]["edges"]
            )
        except RuntimeError:
            return True

    def create_service(self, project_id: str, name: str) -> str:
        """Create a service with no repo/environmentId so Railway creates instances in ALL environments."""
        data = self._gql(
            """mutation($input: ServiceCreateInput!) {
              serviceCreate(input: $input) { id name }
            }""",
            {
                "input": {
                    "projectId": project_id,
                    "name": name,
                }
            },
        )
        return data["serviceCreate"]["id"]

    def delete_service(self, service_id: str) -> None:
        """Delete a service (and all its instances/deployments)."""
        self._gql(
            """mutation($id: String!) {
              serviceDelete(id: $id)
            }""",
            {"id": service_id},
        )

    def connect_service(self, service_id: str, repo: str, branch: str) -> None:
        self._gql(
            """mutation($id: String!, $input: ServiceConnectInput!) {
              serviceConnect(id: $id, input: $input) { id }
            }""",
            {"id": service_id, "input": {"repo": repo, "branch": branch}},
        )

    def set_variables(
        self, project_id: str, env_id: str, service_id: str, variables: dict[str, str]
    ) -> None:
        self._gql(
            "mutation($input:VariableCollectionUpsertInput!){variableCollectionUpsert(input:$input)}",
            {
                "input": {
                    "projectId": project_id,
                    "environmentId": env_id,
                    "serviceId": service_id,
                    "variables": variables,
                }
            },
        )

    def update_instance(
        self,
        service_id: str,
        env_id: str,
        dockerfile_path: str = "",
        build_command: str = "",
        start_command: str = "",
        healthcheck_path: str = "",
        healthcheck_timeout: int = 0,
        cpu_limit: float | None = None,
        memory_limit: int | None = None,
    ) -> None:
        payload: dict[str, Any] = {}
        if dockerfile_path:
            payload["dockerfilePath"] = (
                dockerfile_path if dockerfile_path.startswith("/") else f"/{dockerfile_path}"
            )
        if build_command:
            payload["buildCommand"] = build_command
        if start_command:
            payload["startCommand"] = start_command
        if healthcheck_path:
            payload["healthcheckPath"] = healthcheck_path
        if healthcheck_timeout:
            payload["healthcheckTimeout"] = healthcheck_timeout
        if cpu_limit is not None:
            payload["cpuLimit"] = cpu_limit
        if memory_limit is not None:
            payload["memoryLimit"] = memory_limit
        if not payload:
            return
        self._gql(
            """mutation($s:String!,$e:String!,$input:ServiceInstanceUpdateInput!){
              serviceInstanceUpdate(serviceId:$s,environmentId:$e,input:$input)
            }""",
            {"s": service_id, "e": env_id, "input": payload},
        )

    def create_service_domain(self, service_id: str, env_id: str) -> str:
        """Create a Railway-generated public HTTP endpoint for a service."""
        data = self._gql(
            """mutation($input: ServiceDomainCreateInput!) {
              serviceDomainCreate(input: $input) { id domain }
            }""",
            {"input": {"serviceId": service_id, "environmentId": env_id}},
        )
        return data["serviceDomainCreate"]["domain"]

    def deploy(self, service_id: str, env_id: str) -> None:
        self._gql(
            "mutation($s:String!,$e:String!){serviceInstanceDeploy(serviceId:$s,environmentId:$e)}",
            {"s": service_id, "e": env_id},
        )

    def redeploy(self, service_id: str, env_id: str) -> None:
        self._gql(
            "mutation($s:String!,$e:String!){serviceInstanceRedeploy(serviceId:$s,environmentId:$e)}",
            {"s": service_id, "e": env_id},
        )


class InternalClient:
    """Client for https://backboard.railway.com/graphql/internal."""

    def __init__(self, token: str) -> None:
        self._s = requests.Session()
        self._s.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def _gql(self, query: str, variables: dict, op: str = "") -> dict:
        body: dict[str, Any] = {"query": query, "variables": variables}
        if op:
            body["operationName"] = op
        resp = self._s.post(INTERNAL_API, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if errors := data.get("errors"):
            raise RuntimeError(errors[0]["message"])
        return data["data"]

    def deploy_template(
        self,
        project_id: str,
        env_id: str,
        workspace_id: str,
        template_id: str,
        serialized_config: dict,
    ) -> str:
        data = self._gql(
            """mutation templateDeployV2($input: TemplateDeployV2Input!) {
              templateDeployV2(input: $input) { projectId workflowId }
            }""",
            {
                "input": {
                    "serializedConfig": serialized_config,
                    "templateId": template_id,
                    "workspaceId": workspace_id,
                    "projectId": project_id,
                    "environmentId": env_id,
                    "groupId": None,
                }
            },
            "templateDeployV2",
        )
        return data["templateDeployV2"]["workflowId"]

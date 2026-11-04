#!/usr/bin/env python3

import inspect
import logging
import urllib3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display

from mas.devops.backup import backupResources

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)-20s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

display = Display()


def _backup_resources_compat(
    dynClient, kind, api_version, backup_path, namespace=None, name=None, labels=None, strict_named_only=False, auto_discover_secrets=True
):
    """
    Call backupResources, tolerating older mas-devops releases only when no strict behavior is requested.

    If strict_named_only is set or auto_discover_secrets is disabled, the installed mas-devops
    must support those arguments. Otherwise this raises AnsibleError rather than silently
    falling back to broad (unnamed / auto-discovering) behavior.
    """
    kwargs = {
        "namespace": namespace,
        "name": name,
        "labels": labels,
    }
    strictRequested = strict_named_only or not auto_discover_secrets
    try:
        params = inspect.signature(backupResources).parameters
        has_varkw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
        supportsStrict = "strict_named_only" in params or has_varkw
        supportsDiscovery = "auto_discover_secrets" in params or has_varkw
    except (ValueError, TypeError):
        supportsStrict = supportsDiscovery = False

    if strictRequested and not (supportsStrict and supportsDiscovery):
        raise AnsibleError(
            "Strict named-only backup requires a mas-devops release whose backupResources() supports "
            "'strict_named_only' and 'auto_discover_secrets'. Upgrade mas-devops; refusing to fall back to broad backup behavior."
        )
    if supportsStrict:
        kwargs["strict_named_only"] = strict_named_only
    if supportsDiscovery:
        kwargs["auto_discover_secrets"] = auto_discover_secrets

    try:
        return backupResources(dynClient, kind, api_version, backup_path, **kwargs)
    except TypeError as e:
        if strictRequested or not ("strict_named_only" in str(e) or "auto_discover_secrets" in str(e)):
            raise
        return backupResources(dynClient, kind, api_version, backup_path, namespace=namespace, name=name, labels=labels)


class ActionModule(ActionBase):
    """
    Backup Kubernetes resources based on a list of resource definitions

    Usage Example
    -------------
    tasks:
      - name: "Backup MAS Suite resources"
        ibm.mas_devops.backup_resource:
          backup_resources:
            - namespace: "mas-inst1-core"
              resources:
                - kind: Subscription
                  api_version: operators.coreos.com/v1alpha1
                  name: ibm-mas
                - kind: Suite
                  api_version: core.mas.ibm.com/v1
                  name: inst1
          backup_path: "/backup/mas-suite"
          strict_named_only: true
          auto_discover_secrets: true
    """

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get("host", None)
        api_key = self._task.args.get("api_key", None)

        dynClient = get_api_client(api_key=api_key, host=host)

        backup_resources = self._task.args.get("backup_resources")
        backup_path = self._task.args.get("backup_path")
        strict_named_only = self._task.args.get("strict_named_only", False)
        auto_discover_secrets = self._task.args.get("auto_discover_secrets", True)

        # Strict named-only never auto-discovers Secrets: spec.secretName on cert-manager Certificates/Issuers
        # would otherwise pull in CA key-pair Secrets that are only exportable via explicit opt-in.
        if strict_named_only and auto_discover_secrets:
            display.warning("strict_named_only is enabled: forcing auto_discover_secrets=false")
            auto_discover_secrets = False

        if backup_resources is None or not isinstance(backup_resources, list):
            raise AnsibleError("Error: backup_resources argument must be provided as a list")
        if backup_path is None or backup_path == "":
            raise AnsibleError("Error: backup_path argument was not provided")

        display.v(
            f"Starting backup of MAS resources to '{backup_path}' " f"(strict_named_only={strict_named_only}, auto_discover_secrets={auto_discover_secrets})"
        )

        total_backed_up = 0
        total_failed = 0
        total_not_found = 0
        all_discovered_secrets = set()
        secrets_by_namespace = {}  # Track secrets per namespace
        explicitly_backed_up_secrets = {}  # Track explicitly backed up secrets per namespace
        all_secrets_backed_up_namespaces = set()  # Track namespaces where all secrets were backed up
        failed_resources = []  # Track failed resources with details
        not_found_resources = []  # Track explicitly named resources that do not exist

        # Process each namespace and its resources
        for namespace_config in backup_resources:
            namespace = namespace_config.get("namespace")
            resources = namespace_config.get("resources", [])

            # Namespace can be blank for cluster-scoped resources
            if namespace:
                display.v(f"Processing namespace: {namespace}")
            else:
                display.v("Processing cluster-scoped resources")

            # Process each resource in the namespace (or cluster-scoped)
            for resource_def in resources:
                kind = resource_def.get("kind")
                api_version = resource_def.get("api_version")
                name = resource_def.get("name")
                labels = resource_def.get("labels", [])
                required = bool(resource_def.get("required", False))

                if not kind:
                    display.v("Warning: Skipping resource without kind defined")
                    continue

                if not api_version:
                    raise AnsibleError(f"Error: api_version is required for resource kind '{kind}'")

                if strict_named_only and not name:
                    scope = namespace if namespace else "cluster-scoped"
                    display.error(f"Strict named-only backup error: resource kind '{kind}' in {scope} must have an explicit 'name' specified")
                    total_failed += 1
                    failed_resources.append(
                        {
                            "scope": scope,
                            "kind": kind,
                            "name": "unnamed",
                            "api_version": api_version,
                            "description": f"{kind} (unnamed - rejected by strict_named_only)",
                        }
                    )
                    continue

                # Track explicitly listed Secrets to prevent duplicate backup in auto-discovery
                if kind == "Secret" and namespace:
                    if name:
                        if namespace not in explicitly_backed_up_secrets:
                            explicitly_backed_up_secrets[namespace] = set()
                        explicitly_backed_up_secrets[namespace].add(name)
                    else:
                        all_secrets_backed_up_namespaces.add(namespace)

                # Backup resources (either specific or all of that kind)
                # Pass namespace, name, labels, strict_named_only, and auto_discover_secrets
                backed_up, not_found, failed, discovered_secrets = _backup_resources_compat(
                    dynClient,
                    kind,
                    api_version,
                    backup_path,
                    namespace=namespace,
                    name=name,
                    labels=labels,
                    strict_named_only=strict_named_only,
                    auto_discover_secrets=auto_discover_secrets,
                )
                total_backed_up += backed_up
                total_not_found += not_found
                total_failed += failed

                # Report named resources that were not found; a missing required resource is a failure
                if not_found > 0:
                    scope = namespace if namespace else "cluster-scoped"
                    not_found_resources.append(
                        {"scope": scope, "kind": kind, "name": name if name else "all", "api_version": api_version, "required": required}
                    )
                    if required:
                        total_failed += 1
                        failed_resources.append(
                            {
                                "scope": scope,
                                "kind": kind,
                                "name": name if name else "all",
                                "api_version": api_version,
                                "description": f"{kind}/{name} (required resource not found)",
                            }
                        )

                # Track failed resources with details
                if failed > 0:
                    scope = namespace if namespace else "cluster-scoped"
                    resource_desc = f"{kind}/{name}" if name else f"{kind} (all)"
                    if labels:
                        resource_desc += f" with labels {labels}"
                    failed_resources.append(
                        {"scope": scope, "kind": kind, "name": name if name else "all", "api_version": api_version, "description": resource_desc}
                    )

                # Track discovered secrets by namespace (only if namespace is provided)
                if discovered_secrets and namespace:
                    if namespace not in secrets_by_namespace:
                        secrets_by_namespace[namespace] = set()
                    secrets_by_namespace[namespace].update(discovered_secrets)
                    all_discovered_secrets.update(discovered_secrets)

            display.v(f"Backup complete for named resources: {total_backed_up} resources backed up, {total_not_found} not found, {total_failed} failed")

        # Now backup all discovered secrets per namespace (if auto-discovery is enabled)
        if auto_discover_secrets:
            for ns, secret_names in secrets_by_namespace.items():
                if secret_names:
                    if ns in all_secrets_backed_up_namespaces:
                        display.v(f"Skipping auto-discovery for namespace '{ns}' as all secrets were already backed up")
                        continue

                    explicit_secrets = explicitly_backed_up_secrets.get(ns, set())
                    secrets_to_backup = [s for s in sorted(secret_names) if s not in explicit_secrets]
                    skipped_secrets = [s for s in sorted(secret_names) if s in explicit_secrets]

                    if skipped_secrets:
                        display.v(f"Skipping {len(skipped_secrets)} secret(s) in namespace '{ns}' already explicitly backed up: {', '.join(skipped_secrets)}")

                    if secrets_to_backup:
                        display.v(f"Backing up {len(secrets_to_backup)} discovered secret(s) in namespace '{ns}': {', '.join(secrets_to_backup)}")

                        for secret_name in secrets_to_backup:
                            display.v(f"Backing up discovered secret: {secret_name}")
                            backed_up, not_found, failed, _ = _backup_resources_compat(
                                dynClient,
                                "Secret",
                                "v1",
                                backup_path,
                                namespace=ns,
                                name=secret_name,
                                strict_named_only=strict_named_only,
                                auto_discover_secrets=False,
                            )
                            total_backed_up += backed_up
                            total_not_found += not_found
                            total_failed += failed

                            # Track failed secret backups
                            if failed > 0:
                                failed_resources.append(
                                    {
                                        "scope": ns,
                                        "kind": "Secret",
                                        "name": secret_name,
                                        "api_version": "v1",
                                        "description": f"Secret/{secret_name} (auto-discovered)",
                                    }
                                )

                            if not_found:
                                display.v(f"Warning: Referenced secret '{secret_name}' not found in namespace '{ns}'")

        display.v(f"Backup complete for all: {total_backed_up} resources backed up, {total_not_found} not found, {total_failed} failed")

        # Determine if the backup was successful
        has_failures = total_failed > 0

        return dict(
            message=f"Backed up {total_backed_up} MAS resources" + (f" with {total_failed} failures" if has_failures else ""),
            failed=has_failures,
            changed=False,
            success=not has_failures,
            backed_up_count=total_backed_up,
            not_found_count=total_not_found,
            failed_count=total_failed,
            discovered_secrets_count=len(all_discovered_secrets),
            discovered_secrets=sorted(list(all_discovered_secrets)),
            failed_resources=failed_resources,
            not_found_resources=not_found_resources,
        )

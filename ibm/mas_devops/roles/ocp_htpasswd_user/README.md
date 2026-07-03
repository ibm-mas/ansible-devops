# ocp_htpasswd_user

Add an htpasswd-based user to an OpenShift cluster with a configurable cluster role. The role is designed to be called **once per user** — run it with different `OCP_HTPASSWD_USERNAME` / `OCP_HTPASSWD_PASSWORD` values to add multiple users to the same cluster without overwriting each other.

Every run is idempotent: re-running with the same username updates the bcrypt hash in place (useful for password rotation) without touching other users or identity providers.

## How it works

1. Generates a bcrypt hash of the supplied password using the `htpasswd` binary (`httpd-tools` package, standard in UBI/RHEL-based execution environments)
2. Reads the existing `openshift-config/htpasswd-users` Secret (if it exists), strips any old entry for this username, and appends the new entry
3. Applies the updated Secret
4. Merges the `HTPasswd` identity provider into `OAuth/cluster`, preserving all existing providers (e.g. IBMid on ROKS, GitHub OAuth)
5. Creates a `ClusterRoleBinding` binding the user to the specified cluster role (default: `cluster-admin`)

The plaintext password is **never written to the cluster** — only the bcrypt hash is stored in the Secret.

## Adding multiple users

Call the role multiple times with different env vars. All users share the same htpasswd Secret and IDP entry:

```bash
# First user
export OCP_HTPASSWD_USERNAME="mas-admin1"
export OCP_HTPASSWD_PASSWORD="<secret1>"
ROLE_NAME=ocp_htpasswd_user ansible-playbook ibm.mas_devops.run_role

# Second user — first user is preserved in the same Secret
export OCP_HTPASSWD_USERNAME="mas-admin2"
export OCP_HTPASSWD_PASSWORD="<secret2>"
ROLE_NAME=ocp_htpasswd_user ansible-playbook ibm.mas_devops.run_role

# Add a read-only user
export OCP_HTPASSWD_USERNAME="mas-viewer"
export OCP_HTPASSWD_PASSWORD="<secret3>"
export OCP_HTPASSWD_CLUSTERROLE="view"
ROLE_NAME=ocp_htpasswd_user ansible-playbook ibm.mas_devops.run_role
```

## Password rotation

Re-run with the same username and a new password. The old hash is replaced in the Secret; the ClusterRoleBinding is unchanged.

```bash
export OCP_HTPASSWD_USERNAME="mas-admin1"
export OCP_HTPASSWD_PASSWORD="<new-secret>"
ROLE_NAME=ocp_htpasswd_user ansible-playbook ibm.mas_devops.run_role
```

## Role Variables

### ocp_htpasswd_username

Username for the htpasswd user account.

- **Required**
- Environment Variable: `OCP_HTPASSWD_USERNAME`
- Default: None

**Notes**:
- Use distinct usernames per user so multiple runs accumulate entries rather than overwrite them
- After login, OpenShift creates a `User` resource with this name

### ocp_htpasswd_password

Plaintext password for the user account.

- **Required**
- Environment Variable: `OCP_HTPASSWD_PASSWORD`
- Default: None

**Notes**:
- Used only to derive a bcrypt hash; never written to the cluster in plaintext
- Store in a team vault (e.g. HashiCorp Vault, IBM Secrets Manager, 1Password)
- Re-run the role with the same username and a new password to rotate

### ocp_htpasswd_clusterrole

Cluster role bound to the user. Each user can have a different role — set `OCP_HTPASSWD_CLUSTERROLE` independently on each run.

- Optional
- Environment Variable: `OCP_HTPASSWD_CLUSTERROLE`
- Default: `cluster-admin`

**Valid values**: Any ClusterRole name — `cluster-admin`, `admin`, `edit`, `view`, or a custom role.

### ocp_htpasswd_idp_name

Name of the identity provider entry in `OAuth/cluster`.

- Optional
- Environment Variable: `OCP_HTPASSWD_IDP_NAME`
- Default: `htpasswd-users`

**Notes**:
- Use a consistent value across all runs on the same cluster
- Appears on the OpenShift login page as the provider label
- Renaming this after the first run adds a new IDP entry but does not remove the old one

### ocp_htpasswd_secret_name

Name of the `Secret` in `openshift-config` that holds the htpasswd file.

- Optional
- Environment Variable: `OCP_HTPASSWD_SECRET_NAME`
- Default: `htpasswd-users`

**Notes**:
- All users added by this role share the same Secret
- Use a consistent value across all runs on the same cluster

## Example Playbook

Run via the standard `run_role` playbook:

```bash
export OCP_HTPASSWD_USERNAME="mas-admin"
export OCP_HTPASSWD_PASSWORD="$(vault kv get -field=password secret/mas-admin)"
ROLE_NAME=ocp_htpasswd_user ansible-playbook ibm.mas_devops.run_role
```

Login after the `oauth-openshift` pods have restarted (~30 s):

```bash
oc login https://api.<cluster-domain>:6443 -u mas-admin -p <password>
```

## License

EPL-2.0

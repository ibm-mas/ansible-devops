cp4d_admin_pwd_update
======================

This role will update the password on an existing cp4d instance. By default it will update the password to a randomly generated new password only when the instance is still using the 'initial_admin_password' although using the 'cp4d_admin_password_force_update' variable referenced below will override this to update the password regardless of the current one being used. The new password will be added to the same yaml file that the 'initial_admin_password' was generated into - 'admin-user-details' by default.


Role Variables
--------------

### mas_instance_id
MAS instance identifier associated with the CP4D deployment.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Associates the CP4D password update operation with a specific MAS instance for tracking and organization purposes.

**When to use**: Set when CP4D is deployed as part of a MAS installation to maintain the association between CP4D and MAS.

**Valid values**: Valid MAS instance ID (typically 3-12 lowercase alphanumeric characters)

**Impact**: Used for logging and tracking purposes. Does not affect the password update operation itself.

**Related variables**: [`cp4d_namespace`](#cp4d_namespace)

**Notes**: Optional but recommended for MAS-integrated CP4D deployments to maintain clear associations.

### cp4d_namespace
CP4D instance namespace where password will be updated.

- Optional
- Environment Variable: `CP4D_NAMESPACE`
- Default: `ibm-cpd`

**Purpose**: Specifies the OpenShift namespace where the CP4D instance is deployed.

**When to use**: Use default (`ibm-cpd`) for standard CP4D deployments. Override if CP4D is deployed in a custom namespace.

**Valid values**: Valid Kubernetes namespace name

**Impact**: Determines where to find the CP4D admin credentials secret and where to execute the password update.

**Related variables**: [`cp4d_admin_credentials_secret_name`](#cp4d_admin_credentials_secret_name)

**Notes**: The default `ibm-cpd` is the standard namespace for CP4D deployments.

### cp4d_admin_credentials_secret_name
Kubernetes secret name containing CP4D admin credentials.

- Optional
- Environment Variable: `CP4D_ADMIN_CREDENTIALS_SECRET_NAME`
- Default: `admin-user-details`

**Purpose**: Identifies the Kubernetes secret that stores the CP4D admin password, used to retrieve the current password and store the new one.

**When to use**: Use default (`admin-user-details`) for standard CP4D deployments. Override if using a custom secret name.

**Valid values**: Valid Kubernetes secret name

**Impact**: The role reads the current password from this secret and updates it with the new password after the change.

**Related variables**: [`cp4d_namespace`](#cp4d_namespace), [`cp4d_admin_password`](#cp4d_admin_password)

**Notes**:
- The default `admin-user-details` is the standard secret name for CP4D admin credentials
- Secret must exist in the CP4D namespace
- New password is written back to this same secret

### cp4d_admin_username
CP4D administrator username.

- Optional
- Environment Variable: `CP4D_ADMIN_USERNAME`
- Default: `admin`

**Purpose**: Specifies the CP4D admin user account whose password will be updated.

**When to use**: Use default (`admin`) for standard CP4D deployments. Override if using a custom admin username.

**Valid values**: Valid CP4D username

**Impact**: Determines which user account's password will be changed in CP4D.

**Related variables**: [`cp4d_admin_password`](#cp4d_admin_password), [`cp4d_admin_credentials_secret_name`](#cp4d_admin_credentials_secret_name)

**Notes**: The default `admin` is the standard administrator username for CP4D.

### cp4d_admin_password
Current CP4D admin password (optional).

- Optional
- Environment Variable: `CP4D_ADMIN_PASSWORD`
- Default: None

**Purpose**: Provides the current admin password if not retrievable from the credentials secret.

**When to use**:
- Leave unset (recommended) to auto-retrieve from the credentials secret
- Set explicitly if the secret is not accessible or contains incorrect password
- Useful for manual password recovery scenarios

**Valid values**: Valid CP4D admin password string

**Impact**: When set, this password is used instead of retrieving from the secret. Must match the current CP4D admin password.

**Related variables**: [`cp4d_admin_credentials_secret_name`](#cp4d_admin_credentials_secret_name), [`cp4d_admin_username`](#cp4d_admin_username)

**Notes**:
- **Security**: Avoid setting this in plain text; prefer secret-based retrieval
- The role will attempt to retrieve the password from the secret if not provided
- Only set if you cannot retrieve the password from the secret

### cp4d_admin_password_force_update
Force password update regardless of current password.

- Optional
- Environment Variable: `CP4D_ADMIN_PASSWORD_FORCE_UPDATE`
- Default: `false`

**Purpose**: Controls whether to update the password only if it matches the initial password, or to update it regardless of the current value.

**When to use**:
- Leave as `false` (default) for safe updates that only change initial passwords
- Set to `true` to force password update regardless of current password
- Use `true` for password rotation policies or recovery scenarios

**Valid values**: `true`, `false`

**Impact**:
- `false`: Only updates password if CP4D is still using the initial password from the secret (safe default)
- `true`: Updates password regardless of current value (use with caution)

**Related variables**: [`cp4d_admin_password`](#cp4d_admin_password)

**Notes**:
- **Warning**: Setting to `true` will change the password even if it has been customized
- Default `false` is safer as it only updates passwords that haven't been changed from initial value
- Use `true` for scheduled password rotation or when you need to reset a forgotten password
- New randomly generated password is stored in the credentials secret



Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    cp4d_namespace: ibm-cpd
    cp4d_admin_credentials_secret_name: admin-user-details

    cp4d_admin_username: admin
    cp4d_admin_password: password123
    cp4d_admin_password_force_update: True

  roles:
    - ibm.mas_devops.cp4d_admin_pwd_update
```
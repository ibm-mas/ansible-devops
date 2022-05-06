ocp_github_oauth
================

This role provides to support to configure cluster oauth using GitHub.

!!! warning "Warning"
    Make sure you have configured the oauth app in GitHub organization before use this role. When configuring make sure to use `ibmgithub` as the oauth id. Requires organization admin permission to perform this action.


Role Variables
--------------

- `oauth.github_client_secret_value` Secret value provided by the GitHub oauth app configuration.
- `ouath.github_client_id_value` Client ID value provided by the GitHub oauth app configuration.
- `oauth.github_hostname` can be used to target public GitHub or an enterprise account (e.g. github.ibm.com)
- `oauth.groups` List of groups to be created and its cluster role bindings
- `oauth.groups.name` Defines the name of the group
- `oauth.groups.users` List of users to be added to the group
- `oauth.groups.groups_cluster_rolebindings` List of cluster role bindings to be created for the group
- `oauth.organizations` List of GitHub organizations where the authentication will be performed


Example Playbook
----------------

```yaml
TODO: Add example
```

License
-------

EPL-2.0

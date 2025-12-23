#!/usr/bin/env python3

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError


class ActionModule(ActionBase):

    REQUIRED = {
        "mongodb": {
            "backup":  ["mongodb_instance_name", "mas_backup_dir", "mas_instance_id"], # mongodb_instance_name has a default value
            "restore": ["mongodb_instance_name", "mas_backup_dir", "mongodb_backup_version"]
        },
        "db2": {
            "backup":  ["db2_instance_name", "db2_namespace", "mas_backup_dir", "mas_instance_id"],
            "restore": ["mas_backup_dir", "db2_backup_version"],
            "s3_setup": ["backup_vendor","backup_s3_alias", "backup_s3_endpoint", "backup_s3_bucket", "backup_s3_access_key", "backup_s3_secret_key"]
        }
    }

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        component = self._task.args.get('component', None)
        action = self._task.args.get('action', None)

        if component not in self.REQUIRED:
            raise AnsibleError(f"Unknown component '{component}'. Allowed: {list(self.REQUIRED)}")

        if action not in self.REQUIRED[component]:
            raise AnsibleError(f"Unknown action '{action}' for component '{component}'. Allowed: {list(self.REQUIRED[component])}")
        
        missing_args = []
        for req_arg in self.REQUIRED[component][action]:
            r_arg = self._task.args.get(req_arg, None)
            if r_arg is None or r_arg == '':
                missing_args.append(req_arg)
        
        if len(missing_args) > 0:
            raise AnsibleError(f"Missing required arguments for component '{component}' action '{action}': {missing_args}")
        else:
            return dict(
                changed=False,
                failed=False,
                msg=f"All required arguments for component '{component}' action '{action}' are provided."
                )

        
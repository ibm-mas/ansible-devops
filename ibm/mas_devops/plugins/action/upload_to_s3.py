#!/usr/bin/env python3

import logging
import os
import urllib3
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from mas.devops.backup import uploadToS3

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient

def normalize_endpoint_url(endpoint) -> str|None:
    if not endpoint:
        return endpoint
    if not endpoint.startswith(("http://", "https://")):
        return f"https://{endpoint}"
    return endpoint

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Upload to S3 location"
        ibm.mas_devops.upload_to_s3:
          mas_catalog_version: "{{ catalog_tag }}"
          fail_if_catalog_does_not_exist: true
        register: mas_catalog_metadata
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        file_path = self._task.args.get('file_path', None)
        bucket_name = self._task.args.get('bucket_name', None)
        object_name = self._task.args.get('object_name', None)
        aws_access_key_id = self._task.args.get('aws_access_key_id', None)
        aws_secret_access_key = self._task.args.get('aws_secret_access_key', None)
        endpoint_url = self._task.args.get('endpoint_url', None)
        region_name = self._task.args.get('region_name', None)

        if file_path is None:
            raise AnsibleError(f"Error: file_path argument was not provided")
        if bucket_name is None:
            raise AnsibleError(f"Error: bucket_name argument was not provided")
        if object_name is None:
            raise AnsibleError(f"Error: object_name argument was not provided")
        if aws_access_key_id is None:
            raise AnsibleError(f"Error: aws_access_key_id argument was not provided")
        if aws_secret_access_key is None:
            raise AnsibleError(f"Error: aws_secret_access_key argument was not provided")
        
        endpoint_url = normalize_endpoint_url(endpoint=endpoint_url)

        upload_status = uploadToS3(
            file_path=file_path, bucket_name=bucket_name, object_name=object_name, 
            endpoint_url=endpoint_url, aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key, region_name=region_name
            )
        
        return dict(
            success=upload_status
        )


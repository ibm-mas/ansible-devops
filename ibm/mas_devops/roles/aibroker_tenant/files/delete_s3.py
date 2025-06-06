#!/usr/bin/env python3
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.


# create a new file, ~/.aws/credentials:
# [default]
# aws_access_key_id = YOUR_ACCESS_KEY_ID
# aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

# Create a new file, ~/.aws/config:
# [default]
# region = YOUR_PREFERRED_REGION

import boto3
import sys

s3_resource = boto3.resource('s3')

if len(sys.argv) != 2:
    print("Usage: python delete_bucket.py your-bucket-name")
    sys.exit(1)

if len(sys.argv) == 2 and sys.argv[1] is not None:
    # Need to read from k8s
    YOUR_BUCKET_NAME = sys.argv[1]
else:
    sys.exit(1)

print('will delete the bucket name='+YOUR_BUCKET_NAME)
try:
    print("deleting")
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(YOUR_BUCKET_NAME)
    count = 0
    for key in bucket.objects.all():
        count += 1
        print(key.key)
    print("Number of objects in bucket=", count)
    bucket.object_versions.delete()
    bucket.delete()
    sys.exit(0)
except Exception as e:
    print("Not granted")
    print(e)
    sys.exit(1)

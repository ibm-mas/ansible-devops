#!/usr/bin/env python3
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.


# create a new file, ~/.aws/credentials:
#[default]
#aws_access_key_id = YOUR_ACCESS_KEY_ID
#aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

#Create a new file, ~/.aws/config:
#[default]
#region = YOUR_PREFERRED_REGION


import boto3
import sys
import uuid




if len(sys.argv) != 6:
    print("Usage: python create_bucket.py your-tenant-name access-key secret-key your-region model_id_prefix")
    exit()



if len(sys.argv) == 6 and sys.argv[1] is not None and sys.argv[2] is not None:
    YOUR_BUCKET_NAME= sys.argv[5]+sys.argv[1]
    #print(YOUR_BUCKET_NAME)

    access_key = sys.argv[2]
    secret_key = sys.argv[3]
    region = sys.argv[4]
else:
    exit()

if YOUR_BUCKET_NAME is None:
    print("Usage: python create_bucket.py your-tenant-name access-key secret-key your-region")
    exit()

if region is None:
    print("Usage: python create_bucket.py your-tenant-name access-key secret-key your-region")
    exit()

if access_key is None:
    print("Usage: python create_bucket.py your-tenant-name access-key secret-key your-region")
    exit()

if secret_key is None:
    print("Usage: python create_bucket.py your-tenant-name access-key secret-key your-region")
    exit()



credentials = {
    "aws_access_key_id": access_key,
    "aws_secret_access_key": secret_key
}

try:
    s3_resource = boto3.resource('s3',region_name= region,**credentials)

    # Need to add try/catch
    if region == "us-east-1":
        bucket_response=s3_resource.create_bucket(Bucket=YOUR_BUCKET_NAME)
    else:
    
        bucket_response=s3_resource.create_bucket(Bucket=YOUR_BUCKET_NAME,
                          CreateBucketConfiguration={
                              'LocationConstraint': region})
    

    
    
    print(YOUR_BUCKET_NAME)
except Exception as e:
    print("Error:", e)

#print(bucket_response)
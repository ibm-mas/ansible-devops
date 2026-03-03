#!/bin/bash
# Helper script to run DocumentDB backup playbook
# Usage: ./run_docdb_backup.sh

# Set your variables here or pass them as environment variables
DOCDB_CLUSTER_NAME="${DOCDB_CLUSTER_NAME:-massre-mas-cluster-8-mongo}"
DOCDB_MASTER_USERNAME="${DOCDB_MASTER_USERNAME:-masinst_inst04}"
DOCDB_MASTER_PASSWORD="${DOCDB_MASTER_PASSWORD:-fn9Uh5wZ4KsZy4OZ0OXx}"
AWS_REGION="${AWS_REGION:-us-east-1}"
S3_BUCKET="${S3_BUCKET:-massre-mas-cluster-8-mongo-test}"

# Optional variables
S3_PREFIX="${S3_PREFIX:-docdb-backups}"
LOCAL_BACKUP_DIR="${LOCAL_BACKUP_DIR:-/tmp/docdb-backup}"

# Run the playbook
ansible-playbook ibm/mas_devops/playbooks/docdb_backup_simple.yml \
  -e "docdb_cluster_name=${DOCDB_CLUSTER_NAME}" \
  -e "docdb_master_username=${DOCDB_MASTER_USERNAME}" \
  -e "docdb_master_password=${DOCDB_MASTER_PASSWORD}" \
  -e "aws_region=${AWS_REGION}" \
  -e "s3_bucket=${S3_BUCKET}" \
  -e "s3_prefix=${S3_PREFIX}" \
  -e "local_backup_dir=${LOCAL_BACKUP_DIR}"

# Made with Bob

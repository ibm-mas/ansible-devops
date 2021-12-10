#!/bin/bash

# -----------------------------------------------------------------------------
# Configure Junit report
# -----------------------------------------------------------------------------
export JUNIT_OUTPUT_DIR=/opt/app-root/ansible/junit/
export JUNIT_HIDE_TASK_ARGUMENTS=true
export JUNIT_TASK_CLASS=true

# -----------------------------------------------------------------------------
# Connect to the local cluster
# -----------------------------------------------------------------------------
export K8S_AUTH_HOST=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT_HTTPS
export K8S_AUTH_VERIFY_SSL=false
export K8S_AUTH_API_KEY=$(cat /run/secrets/kubernetes.io/serviceaccount/token)

# -----------------------------------------------------------------------------
# ocp/configure-ocp.yml
# -----------------------------------------------------------------------------
export IBMCLOUD_APIKEY=$(cat /workspace/settings/IBMCLOUD_APIKEY)
export W3_USERNAME=$(cat /workspace/settings/W3_USERNAME)
export ARTIFACTORY_APIKEY=$(cat /workspace/settings/ARTIFACTORY_APIKEY)

# -----------------------------------------------------------------------------
# dependencies/install-mongodb-ce.yml
# -----------------------------------------------------------------------------
export MAS_INSTANCE_ID=$(cat /workspace/settings/MAS_INSTANCE_ID)
export MONGODB_STORAGE_CLASS=$(cat /workspace/settings/MONGODB_STORAGE_CLASS)
export MONGODB_NAMESPACE=$(cat /workspace/settings/MONGODB_NAMESPACE)
export MONGODB_STORAGE_CAPACITY_DATA=$(cat /workspace/settings/MONGODB_STORAGE_CAPACITY_DATA)
export MONGODB_STORAGE_CAPACITY_LOGS=$(cat /workspace/settings/MONGODB_STORAGE_CAPACITY_LOGS)

# -----------------------------------------------------------------------------
# cp4d/install-services-db2.yml
# -----------------------------------------------------------------------------
export CPD_ENTITLEMENT_KEY=$(cat /workspace/settings/CPD_ENTITLEMENT_KEY)
export CPD_NAMESPACE=$(cat /workspace/settings/CPD_NAMESPACE)
export CPD_STORAGE_CLASS=$(cat /workspace/settings/CPD_STORAGE_CLASS)

# -----------------------------------------------------------------------------
# cp4d/create-db2-instance.yml
# -----------------------------------------------------------------------------
export DB2WH_ADMIN_USER=$(cat /workspace/settings/DB2WH_ADMIN_USER)
export DB2WH_ADMIN_PASSWORD=$(cat /workspace/settings/DB2WH_ADMIN_PASSWORD)

# -----------------------------------------------------------------------------
# dependencies/install-amqstreams.yml
# -----------------------------------------------------------------------------
export KAFKA_NAMESPACE=$(cat /workspace/settings/KAFKA_NAMESPACE)
export KAFKA_CLUSTER_NAME=$(cat /workspace/settings/KAFKA_CLUSTER_NAME)
export KAFKA_CLUSTER_SIZE=$(cat /workspace/settings/KAFKA_CLUSTER_SIZE)
export KAFKA_STORAGE_CLASS=$(cat /workspace/settings/KAFKA_STORAGE_CLASS)
export KAFKA_USER_NAME=$(cat /workspace/settings/KAFKA_USER_NAME)

# -----------------------------------------------------------------------------
# sls/install-sls.yml
# -----------------------------------------------------------------------------
export SLS_CATALOG_SOURCE=$(cat /workspace/settings/SLS_CATALOG_SOURCE)
export SLS_CHANNEL=$(cat /workspace/settings/SLS_CHANNEL)
export SLS_NAMESPACE=$(cat /workspace/settings/SLS_NAMESPACE)
export SLS_ICR_CP=$(cat /workspace/settings/SLS_ICR_CP)
export SLS_ICR_CPOPEN=$(cat /workspace/settings/SLS_ICR_CPOPEN)
export SLS_INSTANCE_NAME=$(cat /workspace/settings/SLS_INSTANCE_NAME)
export SLS_ENTITLEMENT_USERNAME=$(cat /workspace/settings/SLS_ENTITLEMENT_USERNAME)
export SLS_ENTITLEMENT_KEY=$(cat /workspace/settings/SLS_ENTITLEMENT_KEY)
export SLS_STORAGE_CLASS=$(cat /workspace/settings/SLS_STORAGE_CLASS)
export SLS_DOMAIN=$(cat /workspace/settings/SLS_DOMAIN)
export SLS_AUTH_ENFORCE=$(cat /workspace/settings/SLS_AUTH_ENFORCE)
export SLS_COMPLIANCE_ENFORCE=$(cat /workspace/settings/SLS_COMPLIANCE_ENFORCE)
export SLS_REGISTRATION_OPEN=$(cat /workspace/settings/SLS_REGISTRATION_OPEN)
export SLS_LICENSE_ID=$(cat /workspace/settings/SLS_LICENSE_ID)

# -----------------------------------------------------------------------------
# bas/install-bas.yaml
# -----------------------------------------------------------------------------
export BAS_NAMESPACE=$(cat /workspace/settings/BAS_NAMESPACE)
export BAS_PERSISTENT_STORAGE_CLASS=$(cat /workspace/settings/BAS_PERSISTENT_STORAGE_CLASS)
export BAS_META_STORAGE_CLASS=$(cat /workspace/settings/BAS_META_STORAGE_CLASS)
export BAS_USERNAME=$(cat /workspace/settings/BAS_USERNAME)
export BAS_PASSWORD=$(cat /workspace/settings/BAS_PASSWORD)
export BAS_GRAFANA_USERNAME=$(cat /workspace/settings/BAS_GRAFANA_USERNAME)
export BAS_GRAFANA_PASSWORD=$(cat /workspace/settings/BAS_GRAFANA_PASSWORD)
export BAS_CONTACT_MAIL=$(cat /workspace/settings/BAS_CONTACT_MAIL)
export BAS_CONTACT_FIRSTNAME=$(cat /workspace/settings/BAS_CONTACT_FIRSTNAME)
export BAS_CONTACT_LASTNAME=$(cat /workspace/settings/BAS_CONTACT_LASTNAME)

# -----------------------------------------------------------------------------
# mas/install-suite.yml
# -----------------------------------------------------------------------------
export MAS_CATALOG_SOURCE=$(cat /workspace/settings/MAS_CATALOG_SOURCE)
export MAS_CHANNEL=$(cat /workspace/settings/MAS_CHANNEL)
export MAS_DOMAIN=$(cat /workspace/settings/MAS_DOMAIN)
export MAS_ICR_CP=$(cat /workspace/settings/MAS_ICR_CP)
export MAS_ICR_CPOPEN=$(cat /workspace/settings/MAS_ICR_CPOPEN)
export MAS_ENTITLEMENT_USERNAME=$(cat /workspace/settings/MAS_ENTITLEMENT_USERNAME)
export MAS_ENTITLEMENT_KEY=$(cat /workspace/settings/MAS_ENTITLEMENT_KEY)
export CIS_CRN=$(cat /workspace/settings/CIS_CRN)
export CIS_SUBDOMAIN=$(cat /workspace/settings/CIS_SUBDOMAIN)
export CIS_EMAIL=$(cat /workspace/settings/CIS_EMAIL)
export CIS_SKIP_DNS_ENTRIES=$(cat /workspace/settings/CIS_SKIP_DNS_ENTRIES)
export CIS_SKIP_CLUSTER_ISSUER=$(cat /workspace/settings/CIS_SKIP_CLUSTER_ISSUER)
export UPDATE_DNS_ENTRIES=$(cat /workspace/settings/UPDATE_DNS_ENTRIES)
export OCP_INGRESS=$(cat /workspace/settings/OCP_INGRESS)
export MAS_CUSTOM_CLUSTER_ISSUER=$(cat /workspace/settings/MAS_CUSTOM_CLUSTER_ISSUER)
export CERTIFICATE_DURATION=$(cat /workspace/settings/CERTIFICATE_DURATION)
export CERTIFICATE_RENEW_BEFORE=$(cat /workspace/settings/CERTIFICATE_RENEW_BEFORE)
export MAS_CATALOG_IMG=$(cat /workspace/settings/MAS_CATALOG_IMG)
export TM_CATALOG_IMG=$(cat /workspace/settings/TM_CATALOG_IMG)

# -----------------------------------------------------------------------------
# mas/configure-app.yml
# -----------------------------------------------------------------------------
export MAS_WORKSPACE_ID=$(cat /workspace/settings/MAS_WORKSPACE_ID)


# The following settings are provided as env vars per-task because they may
# vary for different tasks in the same pipeline
# -----------------------------------------------------------------------------
# - MAS_APP_ID # must be in ClusterTask as it will parameterize install-app task
# - MAS_APP_CATALOG_SOURCE # must be in fvt-env travis, by app, as it varies by environment
# - MAS_APP_CHANNEL # must be in fvt-env travis, by app as it varies by environment
# - MAS_APPWS_COMPONENTS # must be in ClusterTask as it will parameterize configure-app task
# - MAS_CONFIG_DIR # must be in ClusterTask as it will reflect a pipeline workspace

# Settings to support save-junit-to-mongo.py
# -----------------------------------------------------------------------------
export DEVOPS_MONGO_URI=$(cat /workspace/settings/DEVOPS_MONGO_URI)
export TRAVIS_BUILD_NUMBER=$(cat /workspace/settings/TRAVIS_BUILD_NUMBER)

# Print out all env vars
# -----------------------------------------------------------------------------
env | sort

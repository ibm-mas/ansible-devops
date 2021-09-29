#!/bin/bash

# Connect to the local cluster
# -----------------------------------------------------------------------------
export K8S_AUTH_HOST=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT_HTTPS
export K8S_AUTH_VERIFY_SSL=false
export K8S_AUTH_API_KEY=$(cat /run/secrets/kubernetes.io/serviceaccount/token)


# The following settings are provided as env vars per-task because they may
# vary for different tasks in the same pipeline
# -----------------------------------------------------------------------------
# - MAS_CONFIG_DIR
# - MAS_APP_ID
# - MAS_APP_CATALOG_SOURCE
# - MAS_APP_CHANNEL
# - MAS_WORKSPACE_ID


# CloudPak for Data settings
# -----------------------------------------------------------------------------
export CPD_ENTITLEMENT_KEY=$(cat /workspace/settings/CPD_ENTITLEMENT_KEY)
export CPD_STORAGE_CLASS=$(cat /workspace/settings/CPD_STORAGE_CLASS)


# AMQStreams (Kafka) settings
# -----------------------------------------------------------------------------
export KAFKA_NAMESPACE=$(cat /workspace/settings/KAFKA_NAMESPACE)
export KAFKA_CLUSTER_NAME=$(cat /workspace/settings/KAFKA_CLUSTER_NAME)
export KAFKA_CLUSTER_SIZE=$(cat /workspace/settings/KAFKA_CLUSTER_SIZE)
export KAFKA_STORAGE_CLASS=$(cat /workspace/settings/KAFKA_STORAGE_CLASS)
export KAFKA_USER_NAME=$(cat /workspace/settings/KAFKA_USER_NAME)


# MongoDb settings
# -----------------------------------------------------------------------------
export MONGODB_NAMESPACE=$(cat /workspace/settings/MONGODB_NAMESPACE)
export MONGODB_STORAGE_CLASS=$(cat /workspace/settings/MONGODB_STORAGE_CLASS)
export MONGODB_STORAGE_CAPACITY_DATA=$(cat /workspace/settings/MONGODB_STORAGE_CAPACITY_DATA)
export MONGODB_STORAGE_CAPACITY_LOGS=$(cat /workspace/settings/MONGODB_STORAGE_CAPACITY_LOGS)


# SLS settings
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
export SLS_REGISTRATION_KEY=$(cat /workspace/settings/SLS_REGISTRATION_KEY)


# MAS settings
# -----------------------------------------------------------------------------
export MAS_INSTANCE_ID=$(cat /workspace/settings/MAS_INSTANCE_ID)

export MAS_ICR_CP=$(cat /workspace/settings/MAS_ICR_CP)
export MAS_ICR_CPOPEN=$(cat /workspace/settings/MAS_ICR_CPOPEN)
export MAS_ENTITLEMENT_USERNAME=$(cat /workspace/settings/MAS_ENTITLEMENT_USERNAME)
export MAS_ENTITLEMENT_KEY=$(cat /workspace/settings/MAS_ENTITLEMENT_KEY)

export MAS_CATALOG_SOURCE=$(cat /workspace/settings/MAS_CATALOG_SOURCE)
export MAS_CHANNEL=$(cat /workspace/settings/MAS_CHANNEL)
export MAS_DOMAIN=$(cat /workspace/settings/MAS_DOMAIN)


# MAS Settings - CIS Integration
# -----------------------------------------------------------------------------
export CIS_CRN=$(cat /workspace/settings/CIS_CRN)
export CIS_SUBDOMAIN=$(cat /workspace/settings/CIS_SUBDOMAIN)
export IBMCLOUD_APIKEY=$(cat /workspace/settings/IBMCLOUD_APIKEY)
export CIS_EMAIL=$(cat /workspace/settings/CIS_EMAIL)
export CIS_SKIP_DNS_ENTRIES=$(cat /workspace/settings/CIS_SKIP_DNS_ENTRIES)
export CIS_SKIP_CLUSTER_ISSUER=$(cat /workspace/settings/CIS_SKIP_CLUSTER_ISSUER)
export UPDATE_DNS_ENTRIES=$(cat /workspace/settings/UPDATE_DNS_ENTRIES)
export OCP_INGRESS=$(cat /workspace/settings/OCP_INGRESS)
export MAS_CUSTOM_CLUSTER_ISSUER=$(cat /workspace/settings/MAS_CUSTOM_CLUSTER_ISSUER)
export CERTIFICATE_DURATION=$(cat /workspace/settings/CERTIFICATE_DURATION)
export CERTIFICATE_RENEW_BEFORE=$(cat /workspace/settings/CERTIFICATE_RENEW_BEFORE)


# Information about what we are testing
# -----------------------------------------------------------------------------
export TRAVIS_BUILD_NUMBER=$(cat /workspace/settings/TRAVIS_BUILD_NUMBER)


# Credentials to access pre-release container images
# -----------------------------------------------------------------------------
export W3_USERNAME=$(cat /workspace/settings/W3_USERNAME)
export ARTIFACTORY_APIKEY=$(cat /workspace/settings/ARTIFACTORY_APIKEY)


# Print out all env vars
# -----------------------------------------------------------------------------
env | sort

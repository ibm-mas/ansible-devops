# Cluster Certificate Retrieval Guide

This guide provides `oc` commands to fetch cluster ingress certificates from all scenarios and attempts used by the MAS DevOps playbooks.

## Overview

The certificate retrieval process follows two main paths:

1. **Private CA Path** - If the cluster has a private Certificate Authority configured
2. **Signed Certificate Path** - If the cluster uses publicly-signed certificates (with 4 fallback attempts)

---

## Private CA Path

### Retrieve Private CA from Cluster Proxy

```bash
# 1. Check for private CA in cluster Proxy config
oc get proxy cluster -o yaml

# 2. If private CA is found, fetch the ConfigMap with the CA bundle
# (replace CONFIGMAP_NAME with the actual name from the proxy output)
oc get configmap CONFIGMAP_NAME -n openshift-config -o jsonpath='{.data.ca-bundle\.crt}'

# 3. Or get the full ConfigMap to see all data
oc get configmap CONFIGMAP_NAME -n openshift-config -o yaml

# 4. Extract and view certificate details
oc get configmap CONFIGMAP_NAME -n openshift-config -o jsonpath='{.data.ca-bundle\.crt}' | openssl x509 -text -noout
```

---

## Signed Certificate Attempts

### Attempt 1: Default Router Certificate

The most common location for ingress certificates. Uses the `router-certs-default` secret in the `openshift-ingress` namespace.

```bash
# Fetch the certificate (base64 decoded)
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d

# View the full secret
oc get secret router-certs-default -n openshift-ingress -o yaml

# View certificate details
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout

# Check if secret exists
oc get secret router-certs-default -n openshift-ingress

# Use custom secret name via environment variable
export OCP_INGRESS_TLS_SECRET_NAME="my-custom-secret"
oc get secret $OCP_INGRESS_TLS_SECRET_NAME -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d
```

---

### Attempt 2: Cluster Ingress Domain-based Secret

Uses the cluster's Ingress subdomain to identify the certificate secret.

```bash
# Get cluster subdomain
oc get ingress cluster -A -o jsonpath='{.spec.domain}'

# Extract the first part (subdomain)
# Example: if domain is "myapp.example.com", search for secret named "myapp"
SUBDOMAIN=$(oc get ingress cluster -A -o jsonpath='{.spec.domain}' | cut -d'.' -f1)

# Fetch the secret using the subdomain name
oc get secret $SUBDOMAIN -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d

# View full secret
oc get secret $SUBDOMAIN -n openshift-ingress -o yaml

# View certificate details
oc get secret $SUBDOMAIN -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout
```

---

### Attempt 3: IngressController Default Certificate

Uses the default IngressController's specified certificate.

```bash
# Get the IngressController default spec
oc get ingresscontroller default -n openshift-ingress-operator -o yaml

# Extract defaultCertificate.name
SECRET_NAME=$(oc get ingresscontroller default -n openshift-ingress-operator -o jsonpath='{.spec.defaultCertificate.name}')

# Fetch the certificate
oc get secret $SECRET_NAME -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d

# View full secret
oc get secret $SECRET_NAME -n openshift-ingress -o yaml

# View certificate details
oc get secret $SECRET_NAME -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout

# Check if defaultCertificate is defined
oc get ingresscontroller default -n openshift-ingress-operator -o jsonpath='{.spec.defaultCertificate}'
```

---

### Attempt 4: Search by Naming Conventions

Searches all secrets in `openshift-ingress` namespace for certificates matching known naming patterns used by different cluster types (ROSA, IPI, TechZone, etc.).

```bash
# List all secrets in openshift-ingress namespace
oc get secrets -n openshift-ingress

# List all secrets with additional details
oc get secrets -n openshift-ingress -o wide

# Search for secrets ending with "-ingress" (ROSA/ARO clusters)
oc get secrets -n openshift-ingress -o name | grep -E "\-ingress$"

# Search for secrets ending with "-primary-cert-bundle-secret" (IPI installs)
oc get secrets -n openshift-ingress -o name | grep -E "\-primary-cert-bundle-secret$"

# Search for letsencrypt certificates
oc get secret letsencrypt-certs -n openshift-ingress -o name 2>/dev/null || echo "Not found"

# Once identified, fetch the specific secret
oc get secret CLUSTER-NAME-ingress -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d

oc get secret CLUSTER-NAME-primary-cert-bundle-secret -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d

oc get secret letsencrypt-certs -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d
```

---

## Comprehensive Diagnostic Commands

### Quick Summary Check (All Sources at Once)

```bash
# Check all potential certificate sources
echo "=== 1. Router Default Secret ===" 
oc get secret router-certs-default -n openshift-ingress -o name 2>/dev/null || echo "Not found"

echo -e "\n=== 2. All TLS Secrets in openshift-ingress ===" 
oc get secrets -n openshift-ingress --sort-by=.metadata.name

echo -e "\n=== 3. IngressController Default Certificate ===" 
oc get ingresscontroller default -n openshift-ingress-operator -o jsonpath='{.spec.defaultCertificate.name}' && echo ""

echo -e "\n=== 4. Cluster Proxy Trusted CA ===" 
oc get proxy cluster -o jsonpath='{.spec.trustedCA.name}' && echo ""

echo -e "\n=== 5. Cluster Ingress Domain ===" 
oc get ingress cluster -A -o jsonpath='{.spec.domain}' && echo ""
```

### Detailed Secret Inspection

```bash
# List all secrets with their type
oc get secrets -n openshift-ingress -o wide

# Show detailed secret information
oc describe secret router-certs-default -n openshift-ingress

# Export full secret as YAML
oc get secret router-certs-default -n openshift-ingress -o yaml > router-certs-default.yaml

# Check secret keys
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data}' | jq 'keys'
```

### Certificate Analysis Commands

```bash
# Extract and analyze certificate
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d > cert.pem

# View certificate in text format
openssl x509 -in cert.pem -text -noout

# Check certificate validity dates
openssl x509 -in cert.pem -noout -dates

# Check certificate issuer
openssl x509 -in cert.pem -noout -issuer

# Check certificate subject
openssl x509 -in cert.pem -noout -subject

# Check certificate fingerprint
openssl x509 -in cert.pem -noout -fingerprint

# View certificate chain
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl crl2pkcs7 -nocrl | openssl pkcs7 -print_certs -text -noout

# Check for expired DST Root CA X3 certificate
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d | grep -A 1 "issuer=" | grep "DST Root CA X3" && echo "WARNING: DST Root CA X3 found (expired)" || echo "DST Root CA X3 not found"
```

---

## Debugging Commands

### Verify Certificate Secret Contents

```bash
# Check if secret has tls.crt key
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data}' | grep -q "tls.crt" && echo "tls.crt exists" || echo "tls.crt NOT found"

# Count certificates in chain
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d | grep -c "BEGIN CERTIFICATE"

# Verify certificate is valid base64
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d > /dev/null && echo "Valid base64" || echo "Invalid base64"
```

### Check Cluster Configuration

```bash
# Get cluster version
oc get clusterversion version -o jsonpath='{.status.desired.version}'

# Get platform type (helps identify which attempt might work)
oc get infrastructure cluster -o jsonpath='{.status.platformStatus.type}'

# Get all IngressControllers
oc get ingresscontroller -n openshift-ingress-operator

# Check if custom ingress certificate is configured
oc get ingresscontroller default -n openshift-ingress-operator -o jsonpath='{.spec.defaultCertificate}'
```

---

## Environment Variables

The playbook supports customization via environment variables:

```bash
# Set custom ingress TLS secret name (instead of using defaults)
export OCP_INGRESS_TLS_SECRET_NAME="my-custom-secret"

# Include full certificate chain (by default only first cert is used)
export INCLUDE_CLUSTER_INGRESS_CERT_CHAIN="true"
```

---

## Common Patterns by Cluster Type

### OpenShift Managed (ROSA)
```bash
# Usually ends with "-ingress" or "-primary-cert-bundle-secret"
oc get secrets -n openshift-ingress -o name | grep -E "\-ingress$|\-primary-cert-bundle-secret$"
```

### OpenShift on IBM Cloud (ROKS)
```bash
# Often uses letsencrypt-certs or router-certs-default
oc get secret letsencrypt-certs -n openshift-ingress -o name 2>/dev/null || oc get secret router-certs-default -n openshift-ingress -o name
```

### OpenShift on Azure (ARO)
```bash
# May use custom naming or IngressController default
oc get ingresscontroller default -n openshift-ingress-operator -o jsonpath='{.spec.defaultCertificate.name}'
```

### OpenShift IPI (On-premise)
```bash
# Check router-certs-default or cluster domain-based
oc get secret router-certs-default -n openshift-ingress -o name 2>/dev/null || \
SUBDOMAIN=$(oc get ingress cluster -A -o jsonpath='{.spec.domain}' | cut -d'.' -f1) && \
oc get secret $SUBDOMAIN -n openshift-ingress -o name
```

---

## Tips and Troubleshooting

1. **Certificate not found**: Check that you have proper permissions on `openshift-ingress` and `openshift-ingress-operator` namespaces
2. **Base64 decode errors**: Ensure the secret has the `tls.crt` key
3. **Multiple certificates**: A secret may contain multiple certificates in the chain. Use Attempt 4 search to find alternatives
4. **Expired DST Root CA X3**: Check the playbook's filtering logic; this certificate is filtered out automatically by the Ansible playbooks
5. **Private CA used**: If using a private CA, the certificate retrieval differs - check the `openshift-config` namespace instead

---

## Related Files

- Ansible playbook: `ibm/mas_devops/common_tasks/get_ingress_cert.yml`
- Signed cert task: `ibm/mas_devops/common_tasks/get_signed_ingress_cert.yml`

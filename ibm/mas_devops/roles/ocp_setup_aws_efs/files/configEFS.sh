#!/bin/bash

: "${FILE_SYSTEM_ID:?the FILE_SYSTEM_ID env var is required to configure EFS in cluster}"
: "${AWS_REGION:?the AWS_REGION env var is required to configure EFS in cluster}"

FILE_SYSTEM_DNS=$FILE_SYSTEM_ID.efs.$AWS_REGION.amazonaws.com

# Store the EFS variables in a ConfigMap
cat <<EOF > efs_configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: efs-provisioner
data:
  file.system.id: $FILE_SYSTEM_ID
  aws.region: $AWS_REGION
  provisioner.name: openshift.org/aws-efs 
  dns.name: $FILE_SYSTEM_DNS
EOF
oc apply -f efs_configmap.yaml

# --- Configuring authorization for EFS volumes ---

## create service account
oc create serviceaccount efs-provisioner

## create clusterrole.yaml
cat <<EOF > efs_clusterrole.yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: efs-provisioner-runner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
  - apiGroups: ["security.openshift.io"]
    resources: ["securitycontextconstraints"]
    verbs: ["use"]
    resourceNames: ["hostmount-anyuid"]
EOF

## create clusterrolebinding.yaml
cat <<EOF > efs_clusterrolebinding.yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: run-efs-provisioner
subjects:
  - kind: ServiceAccount
    name: efs-provisioner
    namespace: default 
roleRef:
  kind: ClusterRole
  name: efs-provisioner-runner
  apiGroup: rbac.authorization.k8s.io
EOF

## create role.yaml
cat <<EOF > efs_role.yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-efs-provisioner
rules:
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
EOF

## create rolebinding.yaml
cat <<EOF > efs_rolebinding.yaml
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-efs-provisioner
subjects:
  - kind: ServiceAccount
    name: efs-provisioner
    namespace: default 
roleRef:
  kind: Role
  name: leader-locking-efs-provisioner
  apiGroup: rbac.authorization.k8s.io
EOF

## apply permissions
oc create -f efs_clusterrole.yaml,efs_clusterrolebinding.yaml,efs_role.yaml,efs_rolebinding.yaml

# create storageclass
cat <<EOF > efs_storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: aws-efs
provisioner: openshift.org/aws-efs
parameters:
  gidMin: "2048" 
  gidMax: "2147483647" 
  gidAllocate: "true" 
EOF

oc apply -f efs_storageclass.yaml

## Create the EFS provisioner
cat <<EOF > efs_provisioner.yaml
kind: Pod
apiVersion: v1
metadata:
  name: efs-provisioner
spec:
  serviceAccount: efs-provisioner
  containers:
    - name: efs-provisioner
      image: quay.io/external_storage/efs-provisioner:latest
      env:
        - name: PROVISIONER_NAME
          valueFrom:
            configMapKeyRef:
              name: efs-provisioner
              key: provisioner.name
        - name: FILE_SYSTEM_ID
          valueFrom:
            configMapKeyRef:
              name: efs-provisioner
              key: file.system.id
        - name: AWS_REGION
          valueFrom:
            configMapKeyRef:
              name: efs-provisioner
              key: aws.region
        - name: DNS_NAME
          valueFrom:
            configMapKeyRef:
              name: efs-provisioner
              key: dns.name
              optional: true
      volumeMounts:
        - name: pv-volume
          mountPath: /persistentvolumes
  volumes:
    - name: pv-volume
      nfs:
        server: $FILE_SYSTEM_DNS 
        path: / 
EOF

oc apply -f efs_provisioner.yaml

rm efs_provisioner.yaml efs_storageclass.yaml efs_rolebinding.yaml efs_role.yaml efs_clusterrolebinding.yaml efs_clusterrole.yaml efs_configmap.yaml
data "template_file" "portworx_storagecluster" {
  template = <<EOF
kind: StorageCluster
apiVersion: core.libopenstorage.org/v1
metadata:
  name: ${local.px_cluster_id}
  namespace: kube-system
  annotations:%{if var.portworx_essentials.enable}${indent(4, "\nportworx.io/misc-args: \"--oem esse\"")}%{endif}
    portworx.io/is-openshift: "true"%{if var.portworx_ibm.enable}${indent(4, "\nportworx.io/misc-args: \"--oem ibm-icp4d\"")}%{endif}
spec:
  image: portworx/oci-monitor:2.7.0%{if var.portworx_ibm.enable}${indent(2, "\ncustomImageRegistry: ${local.priv_image_registry}")}%{endif}
  imagePullPolicy: Always
  kvdb:
    internal: true
  cloudStorage:
    deviceSpecs:
    - type=gp2,size=${var.disk_size},enc=true,kms=${aws_kms_key.px_key.key_id}
    kvdbDeviceSpec: type=gp2,size=${var.kvdb_disk_size},enc=true,kms=${aws_kms_key.px_key.key_id}
  secretsProvider: ${local.secret_provider}
  stork:
    enabled: true
    args:
      webhook-controller: "false"
  autopilot:
    enabled: true
    providers:
    - name: default
      type: prometheus
      params:
        url: http://prometheus:9090%{if var.px_enable_monitoring}${indent(2, "\nmonitoring:")}
    prometheus:
      enabled: true%{endif}
      exportMetrics: true%{if var.px_enable_csi}${indent(2, "\nfeatureGates:")}
    CSI: "true"%{endif}
  deleteStrategy:
    type: UninstallAndWipe
  env:
  - name: "AWS_ACCESS_KEY_ID"
    value: "${var.aws_access_key_id}"
  - name: "AWS_SECRET_ACCESS_KEY"
    value: "${var.aws_secret_access_key}"
  - name: "AWS_CMK"
    value: "${aws_kms_key.px_key.key_id}"
  - name: "AWS_REGION"
    value: "${var.region}"
%{if var.portworx_essentials.enable}
---
apiVersion: v1
kind: Secret
metadata:
  name: px-essential
  namespace: kube-system
data:
  px-essen-user-id: ${var.portworx_essentials.user_id}
  px-osb-endpoint: ${var.portworx_essentials.osb_endpoint}
%{endif}
EOF
}

data "template_file" "portworx_operator" {
  template = <<EOF
%{if var.portworx_enterprise.enable || var.portworx_essentials.enable}
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  generation: 1
  name: portworx-certified
  namespace: kube-system
spec:
  channel: stable
  installPlanApproval: Automatic
  name: portworx-certified
  source: certified-operators
  sourceNamespace: openshift-marketplace
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: kube-system-operatorgroup
  namespace: kube-system
spec:
  serviceAccount:
    metadata:
      creationTimestamp: null
  targetNamespaces:
  - kube-system
%{endif}
%{if var.portworx_ibm.enable}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: portworx-operator
  namespace: kube-system
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: portworx-operator
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: portworx-operator
subjects:
  - kind: ServiceAccount
    name: portworx-operator
    namespace: kube-system
roleRef:
  kind: ClusterRole
  name: portworx-operator
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: portworx-operator
  namespace: kube-system
spec:
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
    type: RollingUpdate
  replicas: 1
  selector:
    matchLabels:
      name: portworx-operator
  template:
    metadata:
      labels:
        name: portworx-operator
    spec:
      containers:
      - name: portworx-operator
        image: ${local.priv_image_registry}/px-operator:1.4.4
        imagePullPolicy: IfNotPresent
        command:
        - /operator
        - --verbose
        - --driver=portworx
        - --leader-elect=true
        env:
        - name: OPERATOR_NAME
          value: portworx-operator
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: "name"
                    operator: In
                    values:
                    - portworx-operator
              topologyKey: "kubernetes.io/hostname"
      serviceAccountName: portworx-operator
%{endif}
EOF
}

data "template_file" "storage_classes" {
  template = <<EOF
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: portworx-shared-sc
provisioner: kubernetes.io/portworx-volume
parameters:
  repl: "1"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  priority_io: "high"
  sharedv4: "true"
allowVolumeExpansion: true
volumeBindingMode: Immediate
reclaimPolicy: Retain
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: portworx-couchdb-sc
provisioner: kubernetes.io/portworx-volume
parameters:
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  priority_io: "high"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: portworx-elastic-sc
provisioner: kubernetes.io/portworx-volume
parameters:
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  priority_io: "high"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: portworx-solr-sc
provisioner: kubernetes.io/portworx-volume
parameters:
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  priority_io: "high"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: portworx-cassandra-sc
provisioner: kubernetes.io/portworx-volume
parameters:
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  priority_io: "high"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: portworx-kafka-sc
provisioner: kubernetes.io/portworx-volume
parameters:
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  priority_io: "high"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-metastoredb-sc
parameters:
  priority_io: high
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-shared-gp
parameters:
  priority_io: high
  repl: "1"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  sharedv4: "true"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-shared-gp2
parameters:
  priority_io: high
  repl: "2"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  sharedv4: "true"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-shared-gp3
parameters:
  priority_io: high
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  sharedv4: "true"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-db-gp
parameters:
  repl: "1"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-db-gp3
parameters:
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-nonshared-gp
parameters:
  priority_io: high
  repl: "1"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-nonshared-gp2
parameters:
  priority_io: high
  repl: "2"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-gp3-sc
parameters:
  priority_io: high
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
allowVolumeExpansion: true
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-shared-gp-allow
parameters:
  priority_io: high
  repl: "2"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  sharedv4: "true"
  io_profile: "cms"
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
allowVolumeExpansion: true
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-db2-rwx-sc
parameters:
  block_size: 4096b
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  sharedv4: "true"
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
allowVolumeExpansion: true
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-db2-rwo-sc
parameters:
  priority_io: high
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  sharedv4: "false"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
allowVolumeExpansion: true
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-dv-shared-gp
parameters:
  priority_io: high 
  repl: "1"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  shared: "true"
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-assistant
parameters:
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  priority_io: "high"
  block_size: "64k"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
allowVolumeExpansion: true
provisioner: kubernetes.io/portworx-volume
reclaimPolicy: Retain
volumeBindingMode: Immediate
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: portworx-db2-fci-sc
provisioner: kubernetes.io/portworx-volume
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: Immediate
parameters:
  block_size: 512b
  priority_io: high
  repl: "3"%{if var.portworx_enterprise.enable && var.portworx_enterprise.enable_encryption}${indent(2, "\nsecure: \"true\"")}%{endif}
  sharedv4: "false"
  io_profile: "db_remote"
  disable_io_profile_protection: "1"
EOF
}
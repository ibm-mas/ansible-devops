data "template_file" "ocs_olm" {
  template = <<EOF
---
apiVersion: v1
kind: Namespace
metadata:
  labels:
    openshift.io/cluster-monitoring: "true"
  name: openshift-storage
spec: {}
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-storage-operatorgroup
  namespace: openshift-storage
spec:
  targetNamespaces:
  - openshift-storage
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: ocs-operator
  namespace: openshift-storage
  labels:
    operators.coreos.com/ocs-operator.openshift-storage: ''
spec:
  channel: "stable-4.8"
  installPlanApproval: Automatic
  name: ocs-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
}

data "template_file" "ocs_storagecluster" {
  template = <<EOF
apiVersion: ocs.openshift.io/v1
kind: StorageCluster
metadata:
  annotations:
    uninstall.ocs.openshift.io/cleanup-policy: delete
    uninstall.ocs.openshift.io/mode: graceful
  name: ocs-storagecluster
  namespace: openshift-storage
  finalizers:
    - storagecluster.ocs.openshift.io
spec:
  encryption:
    enable: true
  externalStorage: {}
  managedResources:
    cephBlockPools: {}
    cephFilesystems: {}
    cephObjectStoreUsers: {}
    cephObjectStores: {}
  storageDeviceSets:
    - config: {}
      count: 1
      dataPVCTemplate:
        metadata:
          creationTimestamp: null
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 1Ti
          storageClassName: gp2
          volumeMode: Block
        status: {}
      name: ocs-deviceset-gp2
      placement: {}
      portable: true
      replica: 3
      resources: {}
  version: 4.8.0
EOF
}

data "template_file" "ocs_toolbox" {
  template = <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rook-ceph-tools
  namespace: openshift-storage
  labels:
    app: rook-ceph-tools
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rook-ceph-tools
  template:
    metadata:
      labels:
        app: rook-ceph-tools
    spec:
      dnsPolicy: ClusterFirstWithHostNet
      containers:
      - name: rook-ceph-tools
        image: rook/ceph:v1.1.9
        command: ["/tini"]
        args: ["-g", "--", "/usr/local/bin/toolbox.sh"]
        imagePullPolicy: IfNotPresent
        env:
          - name: ROOK_ADMIN_SECRET
            valueFrom:
              secretKeyRef:
                name: rook-ceph-mon
                key: admin-secret
        securityContext:
          privileged: true
        volumeMounts:
          - mountPath: /dev
            name: dev
          - mountPath: /sys/bus
            name: sysbus
          - mountPath: /lib/modules
            name: libmodules
          - name: mon-endpoint-volume
            mountPath: /etc/rook
      hostNetwork: true
      volumes:
        - name: dev
          hostPath:
            path: /dev
        - name: sysbus
          hostPath:
            path: /sys/bus
        - name: libmodules
          hostPath:
            path: /lib/modules
        - name: mon-endpoint-volume
          configMap:
            name: rook-ceph-mon-endpoints
            items:
            - key: data
              path: mon-endpoints
EOF
}

data "template_file" "ocs_machineset" {
  template = <<EOF
%{if var.ocs.dedicated_nodes && length(var.ocs.dedicated_node_zones) > 0}
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: CLUSTERID
  name: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[0]}
  namespace: openshift-machine-api
spec:
  replicas: ${length(var.ocs.dedicated_node_zones) == 1 ? 3 : 1 }
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: CLUSTERID
      machine.openshift.io/cluster-api-machineset: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[0]}
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: CLUSTERID
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[0]}
    spec:
      taints:
      - effect: NoSchedule
        key: node.ocs.openshift.io/storage
        value: "true"
      metadata:
        labels:
          cluster.ocs.openshift.io/openshift-storage: ""
          node-role.kubernetes.io/infra: ""
          node-role.kubernetes.io/worker: ""
          role: storage-node
      providerSpec:
        value:
          ami:
            id: ${local.ocs_ami_id}
          apiVersion: awsproviderconfig.openshift.io/v1beta1
          blockDevices:
          - ebs:
              encrypted: true
              iops: 2000
              kmsKey:
                arn: "${aws_kms_key.ocs_key.arn}"
              volumeSize: 300
              volumeType: io1
          credentialsSecret:
            name: aws-cloud-credentials
          deviceIndex: 0
          iamInstanceProfile:
            id: CLUSTERID-worker-profile
          instanceType: ${var.ocs.dedicated_node_instance_type}
          kind: AWSMachineProviderConfig
          metadata:
            creationTimestamp: null
          placement:
            region: ${var.region}
          securityGroups:
          - filters:
            - name: tag:Name
              values:
              - CLUSTERID-worker-sg
          subnet:
            id: ${var.ocs.dedicated_node_subnet_ids[0]}
          tags:
          - name: kubernetes.io/cluster/CLUSTERID
            value: owned
          userDataSecret:
            name: worker-user-data
%{endif}
%{if var.ocs.dedicated_nodes && length(var.ocs.dedicated_node_zones) > 1}
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: CLUSTERID
  name: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[1]}
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: CLUSTERID
      machine.openshift.io/cluster-api-machineset: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[1]}
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: CLUSTERID
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[1]}
    spec:
      taints:
      - effect: NoSchedule
        key: node.ocs.openshift.io/storage
        value: "true"
      metadata:
        labels:
          cluster.ocs.openshift.io/openshift-storage: ""
          node-role.kubernetes.io/infra: ""
          node-role.kubernetes.io/worker: ""
          role: storage-node
      providerSpec:
        value:
          ami:
            id: ${local.ocs_ami_id}
          apiVersion: awsproviderconfig.openshift.io/v1beta1
          blockDevices:
          - ebs:
              encrypted: true
              iops: 2000
              kmsKey:
                arn: "${aws_kms_key.ocs_key.arn}"
              volumeSize: 300
              volumeType: io1
          credentialsSecret:
            name: aws-cloud-credentials
          deviceIndex: 0
          iamInstanceProfile:
            id: CLUSTERID-worker-profile
          instanceType: ${var.ocs.dedicated_node_instance_type}
          kind: AWSMachineProviderConfig
          metadata:
            creationTimestamp: null
          placement:
            region: ${var.region}
          securityGroups:
          - filters:
            - name: tag:Name
              values:
              - CLUSTERID-worker-sg
          subnet:
            id: ${var.ocs.dedicated_node_subnet_ids[1]}
          tags:
          - name: kubernetes.io/cluster/CLUSTERID
            value: owned
          userDataSecret:
            name: worker-user-data
%{endif}
%{if var.ocs.dedicated_nodes && length(var.ocs.dedicated_node_zones) > 2}
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: CLUSTERID
  name: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[2]}
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: CLUSTERID
      machine.openshift.io/cluster-api-machineset: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[2]}
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: CLUSTERID
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: CLUSTERID-workerocs-${var.ocs.dedicated_node_zones[2]}
    spec:
      taints:
      - effect: NoSchedule
        key: node.ocs.openshift.io/storage
        value: "true"
      metadata:
        labels:
          cluster.ocs.openshift.io/openshift-storage: ""
          node-role.kubernetes.io/infra: ""
          node-role.kubernetes.io/worker: ""
          role: storage-node
      providerSpec:
        value:
          ami:
            id: ${local.ocs_ami_id}
          apiVersion: awsproviderconfig.openshift.io/v1beta1
          blockDevices:
          - ebs:
              encrypted: true
              iops: 2000
              kmsKey:
                arn: "${aws_kms_key.ocs_key.arn}"
              volumeSize: 300
              volumeType: io1
          credentialsSecret:
            name: aws-cloud-credentials
          deviceIndex: 0
          iamInstanceProfile:
            id: CLUSTERID-worker-profile
          instanceType: ${var.ocs.dedicated_node_instance_type}
          kind: AWSMachineProviderConfig
          metadata:
            creationTimestamp: null
          placement:
            region: ${var.region}
          securityGroups:
          - filters:
            - name: tag:Name
              values:
              - CLUSTERID-worker-sg
          subnet:
            id: ${var.ocs.dedicated_node_subnet_ids[2]}
          tags:
          - name: kubernetes.io/cluster/CLUSTERID
            value: owned
          userDataSecret:
            name: worker-user-data
---
%{endif}
EOF
}
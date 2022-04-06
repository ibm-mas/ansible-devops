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
  namespace: openshift-storage
  name: ocs-storagecluster
  finalizers:
    - storagecluster.ocs.openshift.io
spec:
  externalStorage: {}
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
          storageClassName: managed-premium
          volumeMode: Block
        status: {}
      name: ocs-deviceset
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
      # if hostNetwork: false, the "rbd map" command hangs, see https://github.com/rook/rook/issues/2021
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

data "template_file" "ocs_machineset_singlezone" {
  template = <<EOF
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
  name: REPLACE_CLUSTERID-workerocs-REPLACE_REGION
  namespace: openshift-machine-api
spec:
  replicas: 3
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
      machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION
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
          apiVersion: azureproviderconfig.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/REPLACE_CLUSTERID-rg/providers/Microsoft.Compute/images/REPLACE_CLUSTERID
            sku: ""
            version: ""
          kind: AzureMachineProviderSpec
          location: REPLACE_REGION
          managedIdentity: REPLACE_CLUSTERID-identity
          metadata:
            creationTimestamp: null
          networkResourceGroup: REPLACE_VNET_RG
          osDisk:
            diskSizeGB: 512
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: REPLACE_CLUSTERID
          resourceGroup: REPLACE_CLUSTERID-rg
          subnet: REPLACE_WORKER_SUBNET
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_D16s_v3
          vnet: REPLACE_VNET_NAME
          zone: ""
EOF
}

data "template_file" "ocs_machineset_multizone" {
  template = <<EOF
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
  name: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-1
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
      machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-1
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-1
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
          apiVersion: azureproviderconfig.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/REPLACE_CLUSTERID-rg/providers/Microsoft.Compute/images/REPLACE_CLUSTERID
            sku: ""
            version: ""
          kind: AzureMachineProviderSpec
          location: REPLACE_REGION
          managedIdentity: REPLACE_CLUSTERID-identity
          metadata:
            creationTimestamp: null
          networkResourceGroup: REPLACE_VNET_RG
          osDisk:
            diskSizeGB: 512
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: REPLACE_CLUSTERID
          resourceGroup: REPLACE_CLUSTERID-rg
          subnet: REPLACE_WORKER_SUBNET
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_D16s_v3
          vnet: REPLACE_VNET_NAME
          zone: "1"
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
  name: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-2
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
      machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-2
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-2
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
          apiVersion: azureproviderconfig.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/REPLACE_CLUSTERID-rg/providers/Microsoft.Compute/images/REPLACE_CLUSTERID
            sku: ""
            version: ""
          kind: AzureMachineProviderSpec
          location: REPLACE_REGION
          managedIdentity: REPLACE_CLUSTERID-identity
          metadata:
            creationTimestamp: null
          networkResourceGroup: REPLACE_VNET_RG
          osDisk:
            diskSizeGB: 512
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: REPLACE_CLUSTERID
          resourceGroup: REPLACE_CLUSTERID-rg
          subnet: REPLACE_WORKER_SUBNET
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_D16s_v3
          vnet: REPLACE_VNET_NAME
          zone: "2"
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
  name: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-3
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
      machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-3
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: REPLACE_CLUSTERID
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: REPLACE_CLUSTERID-workerocs-REPLACE_REGION-3
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
          apiVersion: azureproviderconfig.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/REPLACE_CLUSTERID-rg/providers/Microsoft.Compute/images/REPLACE_CLUSTERID
            sku: ""
            version: ""
          kind: AzureMachineProviderSpec
          location: REPLACE_REGION
          managedIdentity: REPLACE_CLUSTERID-identity
          metadata:
            creationTimestamp: null
          networkResourceGroup: REPLACE_VNET_RG
          osDisk:
            diskSizeGB: 512
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: REPLACE_CLUSTERID
          resourceGroup: REPLACE_CLUSTERID-rg
          subnet: REPLACE_WORKER_SUBNET
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_D16s_v3
          vnet: REPLACE_VNET_NAME
          zone: "3"
EOF
}
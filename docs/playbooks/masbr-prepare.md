# Preparing MAS Backup/Restore Test Environment 

We will prepare environment for testing the MAS backup and restore:

- Set up MinIO object storage for saving the backup files
- Run playbook in [ibmmas/cli](https://quay.io/repository/ibmmas/cli) container, and create k8s Job in OpenShift cluster for running the backup/restore jobs.

## Deploy MinIO object storage

If you don't have a object storage for testing, you can deploy the MinIO object storage in the cluster.

Use `oc login` command to connect to the OpenShift cluster which you want to deploy the MinIO object storage.

```
$ oc login --token=sha256~KBcefFVyxWZTz3f4mmBwNa4aajswGYdK9c6BwyDycIw --server=https://api.lubanbj5.cdl.ibm.com:6443
```

Create a `deployment.yaml` file with below content:

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: minio

---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: minio-config-pvc
  namespace: minio
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
  storageClassName: ocs-storagecluster-cephfs
  volumeMode: Filesystem

---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: minio-storage-pvc
  namespace: minio
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: ocs-storagecluster-cephfs
  volumeMode: Filesystem

---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: minio
  namespace: minio
  labels:
    component: minio
spec:
  replicas: 1
  selector:
    matchLabels:
      component: minio
  template:
    metadata:
      creationTimestamp: null
      labels:
        component: minio
    spec:
      volumes:
        - name: storage
          persistentVolumeClaim:
            claimName: minio-storage-pvc
        - name: config
          persistentVolumeClaim:
            claimName: minio-config-pvc
      containers:
        - resources: {}
          terminationMessagePath: /dev/termination-log
          name: minio
          env:
            - name: MINIO_ACCESS_KEY
              value: minio
            - name: MINIO_SECRET_KEY
              value: minio123
          ports:
            - containerPort: 9000
              protocol: TCP
            - containerPort: 9001
              protocol: TCP
          imagePullPolicy: IfNotPresent
          volumeMounts:
            - name: storage
              mountPath: /storage
            - name: config
              mountPath: /config
          terminationMessagePolicy: File
          image: minio/minio:latest
          args:
            - server
            - /storage
            - '--console-address'
            - ':9001'
            - '--config-dir=/config'
          securityContext: 
            runAsNonRoot: true
            allowPrivilegeEscalation: false
            seccompProfile:
              type: RuntimeDefault
            capabilities:
              drop:
                - ALL
      restartPolicy: Always
      terminationGracePeriodSeconds: 30
      dnsPolicy: ClusterFirst
      schedulerName: default-scheduler
  strategy:
    type: Recreate
  revisionHistoryLimit: 10
  progressDeadlineSeconds: 600

---
kind: Service
apiVersion: v1
metadata:
  name: minio
  namespace: minio
spec:
  ipFamilies:
    - IPv4
  ports:
    - name: api
      protocol: TCP
      port: 9000
      targetPort: 9000
    - name: console
      protocol: TCP
      port: 9001
      targetPort: 9001
  internalTrafficPolicy: Cluster
  type: ClusterIP
  ipFamilyPolicy: SingleStack
  sessionAffinity: None
  selector:
    component: minio
```

Run below command to deploy MinIO:

```
oc apply -f deployment.yaml
```

Create a script with below content for adding routes for MinIO:

```shell
domain=$(oc get DNS cluster --no-headers -o=custom-columns=DOMAIN:.spec.baseDomain)

cat <<EOF | oc apply -f -
---
kind: Route
apiVersion: route.openshift.io/v1
metadata:
  name: minio-api
  namespace: minio
spec:
  host: minio-api.apps.${domain}
  to:
    kind: Service
    name: minio
    weight: 100
  port:
    targetPort: api
  wildcardPolicy: None
---
kind: Route
apiVersion: route.openshift.io/v1
metadata:
  name: minio-webui
  namespace: minio
spec:
  host: minio-webui.apps.${domain}
  to:
    kind: Service
    name: minio
    weight: 100
  port:
    targetPort: console
  wildcardPolicy: None
EOF

echo ""
echo "API:  http://minio-api.apps.${domain}"
echo "Web:  http://minio-webui.apps.${domain}"
echo "      minio/minio123"
echo ""
```

Login MinIO web console with the link and credentail output by above script, and then in the MinIO web console:

- Create a access key and write down the generated  `Access Key` and `Secret Key`.
- Create a bucket with the name `mas-backup`

## Create a Rclone configuration file
Sample configuration file path: `/home/reacher/.config/rclone/rclone.conf`  
Sample configuration file content:

```
[masbr]
type = s3
provider = Minio
endpoint = http://minio-api.apps.lubanbj5.cdl.ibm.com
access_key_id = SKgkonoD70aLGev4H1dV
secret_access_key = 46kGtXnyERhHMRnz08K5U9yltD7Ds9P3VeU4cV9A
region = minio
``` 

You also can install [Rclone](https://rclone.org/downloads/#script-download-and-install) tool and create the configuration file by running the `rclone config` command. For more information about the rclone commands and configuration file format, please refer to the [Rclone doc](https://rclone.org/s3/#configuration). 

## Run MAS CLI docker container
You can run a playbook/role either in the MAS CLI docker container, or in your local workstation. For more details, please refer to [this doc](../index.md#running-in-docker).

In this example, we will use docker container to run playbooks and roles. Create a `.env` file to keep some common environment variables. We will run the MAS CLI docker container with this `.env` file later, so that you don't need to explicitly set these environment variables in the container every time after it started.

Sample env file path: `/tmp/run_task_job.env`  
Sample env file content: 

```
MASBR_STORAGE_TYPE=cloud
MASBR_STORAGE_CLOUD_RCLONE_FILE=/mnt/configmap/rclone.conf
MASBR_STORAGE_CLOUD_RCLONE_NAME=masbr
MASBR_STORAGE_CLOUD_BUCKET=mas-backup
```

For more information about these environment variables, please refer to [this doc](masbr-storage.md#use-cloud-object-storage).

Run MAS CLI docker container:
```
podman run -ti -v /home/reacher/.config/rclone:/mnt/configmap --env-file=/tmp/run_task_job.env --pull always quay.io/ibmmas/cli
```

## Login to cluster
In the container, run `oc login` command to login to the cluster which you want to run the backup/restore job.
```
$ oc login --token=sha256~KBcefFVyxWZTz3f4mmBwNa4aajswGYdK9c6BwyDycIw --server=https://api.lubanbj5.cdl.ibm.com:6443
```

Next, you can run the playbooks and roles to create the MAS backup/restore jobs, please refer to corresponding playbook/role doc for details.

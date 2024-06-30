Preparing MAS Backup/Restore Test Environment
===============================================================================
We will prepare environment for testing the MAS backup and restore:

- Set up MinIO object storage for saving the backup files
- Run playbook in [ibmmas/cli](https://quay.io/repository/ibmmas/cli) container, and create k8s Job in OpenShift cluster for running the backup/restore jobs.


Deploy MinIO object storage
-------------------------------------------------------------------------------
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


Create a Rclone configuration file
-------------------------------------------------------------------------------
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


Run MAS CLI docker container
-------------------------------------------------------------------------------
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


Login to cluster
-------------------------------------------------------------------------------
In the container, run `oc login` command to login to the cluster which you want to run the backup/restore job.
```
$ oc login --token=sha256~KBcefFVyxWZTz3f4mmBwNa4aajswGYdK9c6BwyDycIw --server=https://api.lubanbj5.cdl.ibm.com:6443
```

Next, you can run the playbooks and roles to create the MAS backup/restore jobs, please refer to corresponding playbook/role doc for details.









More Examples
-------------------------------------------------------------------------------
!!! important
    Before you proceed with the following steps, please refer to [this doc](masbr-prepare.md) to prepare the testing environment.

All above playbooks support the [common environment variables](masbr-vars.md) to backup the MAS components in a similar way. In this example, we will use Manage to demonstrate how to:

- [Taking an on-demand full backup](#taking-a-full-backup)
- [Taking an on-demand incremental backup based on the latest full backup](#taking-an-incremental-backup)
- [Creating a scheduled backup job](#creating-a-scheduled-backup-job)

### Taking a full backup
Run below commands in the container to take a full backup:
```shell
$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev
$ export DB2_INSTANCE_NAME=mas-main-masdev-manage

$ ansible-playbook ibm.mas_devops.backup_manage
```

The playbook will create a k8s Job in the OpenShift cluster to run the backup process, you can get the backup version and job link from the output:
```txt
TASK [Summary of backup job] ***************************************************************************************************************************************************************
ok: [localhost] =>
  msg:
  - Backup version ..................... 20240623062652
  - Backup from ........................ <none>
  - Job name ........................... backup-20240623062652-20240623062657
  - Job link ........................... https://console-openshift-console.apps.lubanbj5.cdl.ibm.com/k8s/ns/mas-main-manage/jobs/backup-20240623062652-20240623062657
```

Copy above job link and open it in the web browser to check the backup progress.

After the backup job is completed, you can login to the object storage web console to check the backed up files, or run below rclone commands in the container to have some checks:

- List the backup folders created by this backup job in the object storage:
```shell
$ export BACKUP_VERSION=20240623062652
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} lsd ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups | grep ${BACKUP_VERSION}
```

If the backup job is completed successfully, you will get the output similar to the following:
```text
           0 2000-01-01 00:00:00        -1 core-main-full-20240623062652-Completed
           0 2000-01-01 00:00:00        -1 db2-mas-main-masdev-manage-full-20240623062652-Completed
           0 2000-01-01 00:00:00        -1 manage-main-full-20240623062652-Completed
           0 2000-01-01 00:00:00        -1 mongodb-main-full-20240623062652-Completed
```

- Further check the files in a backup folder:
```shell
$ export FOLDER_NAME=db2-mas-main-masdev-manage-full-20240623062652-Completed
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} tree ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups/${FOLDER_NAME}
```

You will get the output similar to the following:
```text
/
├── backup.yml
├── database
│   └── db2-mas-main-masdev-manage-full-20240623062652.tar.gz
└── log
    ├── copy-20240623062652-20240623063515-db2-database-log.tar.gz
    ├── copy-20240623062652-20240623063820-db2-database-log.tar.gz
    ├── db2-backup-log.tar.gz
    └── db2-mas-main-masdev-manage-full-20240623062652-ansible-log.tar.gz

2 directories, 6 files
```

### Taking an incremental backup
!!! tip
    For more information about incremental backup, please refer to the doc for [MASBR_BACKUP_TYPE](masbr-vars.md#masbr_backup_type) and [MASBR_BACKUP_FROM_VERSION](masbr-vars.md#masbr_backup_from_version).

In the MAS CLI container, run below command to take an incremental backup based on the latest full backup:
```shell
$ export MASBR_BACKUP_TYPE=incr

$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev
$ export DB2_INSTANCE_NAME=mas-main-masdev-manage

$ ansible-playbook ibm.mas_devops.backup_manage
```

The playbook will create a k8s Job in the OpenShift cluster, you can get the backup version and job link from the output:
```text
TASK [Summary of backup job] ***************************************************************************************************************************************************************
ok: [localhost] =>
  msg:
  - Backup version ..................... 20240623065309
  - Backup from ........................ manage-main-full-20240623062652
  - Job name ........................... backup-20240623065309-20240623065328
  - Job link ........................... https://console-openshift-console.apps.lubanbj5.cdl.ibm.com/k8s/ns/mas-main-manage/jobs/backup-20240623065309-20240623065328
```

The `Backup from` in the above outputs indicate which full backup this incremental backup is based on.

Copy above job link and open it in the web browser to check the backup progress.

After the backup job is completed, you can login to the object storage web console to check the backed up files, or run below rclone commands in the container to have some checks:

- List the backup folders created by this backup job in the object storage:
```shell
$ export BACKUP_VERSION=20240623065309
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} lsd ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups | grep ${BACKUP_VERSION}
```

If the backup job is completed successfully, you will get the output similar to the following:
```
           0 2000-01-01 00:00:00        -1 core-main-incr-20240623065309-Completed
           0 2000-01-01 00:00:00        -1 db2-mas-main-masdev-manage-incr-20240623065309-Completed
           0 2000-01-01 00:00:00        -1 manage-main-incr-20240623065309-Completed
           0 2000-01-01 00:00:00        -1 mongodb-main-incr-20240623065309-Completed
```

- Further check the backup job details:
```shell
$ export FOLDER_NAME=db2-mas-main-masdev-manage-incr-20240623065309-Completed
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} cat ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups/${FOLDER_NAME}/backup.yml
```

You will get the output similar to the following:
```yaml
---
kind: Backup
name: "db2-mas-main-masdev-manage-incr-20240623065309"
version: "20240623065309"
type: "incr"
from: "db2-mas-main-masdev-manage-full-20240623062652"
source:
  domain: "lubanbj5.cdl.ibm.com"
  suite: ""
  instance: "main"
  workspace: "masdev"
component:
  name: "db2"
  instance: "mas-main-masdev-manage"
  namespace: "db2u"
data:
  - seq: "1"
    type: "database"
    phase: "Completed"
status:
  phase: "Completed"
  startTimestamp: "2024-06-23T06:56:21"
  completionTimestamp: "2024-06-23T07:01:46"
```

### Creating a scheduled backup job
!!! tip
    For more information about scheduled backup, please refer to the doc for [MASBR_BACKUP_SCHEDULE](masbr-vars.md#masbr_backup_schedule) and [MASBR_BACKUP_TIMEZONE](masbr-vars.md#masbr_backup_timezone).

In below example, we will create a scheduled backup job to run at 1:00 a.m. Monday through Friday:
```shell
$ export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
$ export MASBR_BACKUP_TIMEZONE="Asia/Shanghai"

$ export MASBR_BACKUP_TYPE=incr

$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev
$ export DB2_INSTANCE_NAME=mas-main-masdev-manage

$ ansible-playbook ibm.mas_devops.backup_manage
```

The playbook will create a k8s CronJob in the OpenShift cluster, you can get the backup version and job link from the output:
```text
TASK [Summary of backup job] ***************************************************************************************************************************************************************
ok: [localhost] =>
  msg:
  - Backup version ..................... 20240623071218
  - Backup from ........................ manage-main-full-20240623062652
  - Job name ........................... schedule-20240623071218-20240623071236
  - Job link ........................... https://console-openshift-console.apps.lubanbj5.cdl.ibm.com/k8s/ns/mas-main-manage/cronjobs/schedule-20240623071218-20240623071236
```

You can copy the above job link and open it in the web browser to check the CronJob running status.

If you want to change the schedule of this CronJob after it created, you can get necessary information from above output and run below command:
```shell
$ JOB_NAME=schedule-20240623071218-20240623071236
$ JOB_NAMESPACE=mas-main-manage
$ JOB_SCHEDULE="30 15 * * *"
$ oc patch CronJob ${JOB_NAME} -n ${JOB_NAMESPACE} -p "{\"spec\": {\"schedule\": \"${JOB_SCHEDULE}\"}}"
```


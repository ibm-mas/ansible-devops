# IBM Maximo Application Suite Tekton Pipelines

These pipelines are all powered by the container image in this same repository, and provide an alternative to running our Ansible roles and playbooks locally.  With Pipelines you can configure your own devops processes directly in the cluster and chain togther the building blocks (ClusterTasks) that we have created.

To learn more about Tekton refer to the excellent material here: https://redhat-scholars.github.io/tekton-tutorial/tekton-tutorial/index.html

## ClusterTasks

# CP4D Management
- [Create Db2 Warehouse Instance](tasks/dependencies/create-db2-instance.yaml)
- [Install CP4D with Db2 Warehouse service enabled](tasks/dependencies/install-db2.yaml)
- [Install CP4D with Db2 Warehouse & Watson Studio services enabled](tasks/dependencies/install-fullstack.yaml)
- [Install CP4D with Watson Studio services enabled](tasks/dependencies/install-watsonstudio.yaml)

### Dependency Management
- [Install AMQStreams](tasks/dependencies/install-amqstreams.yaml)
- [Install Behavior Analytics Service](tasks/bas/install-bas.yaml)
- [Install MongoDb CE](tasks/dependencies/install-mongodb-ce.yaml)
- [Install IBM Suite License Service](tasks/sls/install-sls.yaml)

### MAS Management
- [Configure Application](tasks/mas/configure-app.yaml)
- [Configure MAS Core](tasks/mas/configure-suite.yaml)
- [Manage Db2 Database Configuration Hack](tasks/mas/hack-manage-db2.yaml)
- [Install Application](tasks/mas/install-app.yaml)
- [Install MAS Core](tasks/mas/install-suite.yaml)

### OCP Management
- [Configure OCP Cluster for MAS](tasks/ocp/configure-ocp.yaml)


### Usage

### 1. Provision Cluster and Install OpenShift Pipelines Operator
After provisioning and logging into the cluster, you can use the install script provided: `bin/install-pipelines.sh`:

```bash
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
ansible-playbook playbooks/ocp/provision-roks.yml
ansible-playbook playbooks/cp4d/hack-worker-nodes.yml
bin/install-pipelines.sh
```


# 2. Build and Install the MAS Pipeline Task Definitions
```
export DEV_MODE=true
export VERSION=5.1.0
pipelines/bin/build-pipelines.sh

cd pipelines
oc apply -f ibm-mas_devops-clustertasks-5.1.0.yaml
```

# 3. Install and run the MAS Sample Pipeline
Modify the [sample-pipelinesettings.yaml](samples/sample-pipelinesettings.yaml) to populate it with your own settings before applying it to the cluster, and optionally customize the parameters in [sample-pipelinerun-mas86.yaml](samples/sample-pipelinerun-mas86.yaml) if you wish to adjust the subscription channels for the MAS applications.

```bash
oc new-project mas-sample-pipelines
oc apply -f samples/sample-pipelinesettings.yaml

oc create secret generic pipeline-additional-configs \
  --from-file=/home/david/masconfig/workspace_masdev.yaml

oc create secret generic pipeline-sls-entitlement \
  --from-file=/home/david/masconfig/entitlement.lic

oc apply -f samples/sample-pipeline.yaml
oc create -f samples/sample-pipelinerun-mas86.yaml
```

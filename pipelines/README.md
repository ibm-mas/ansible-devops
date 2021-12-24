# IBM Maximo Application Suite Tekton Pipelines

These pipelines are all powered by the container image in this same repository, and provide an alternative to running our Ansible roles and playbooks locally.  With Pipelines you can configure your own devops processes directly in the cluster and chain togther the building blocks (ClusterTasks) that we have created.

To learn more about Tekton refer to the excellent material here: https://redhat-scholars.github.io/tekton-tutorial/tekton-tutorial/index.html

## ClusterTasks

# CP4D Management
- Install CP4D - dependencies/install-cp4d.yaml
- Install Db2 Warehouse (via undocumented API!) - dependencies/install-db2-api.yaml
- Install Db2 Warehouse - dependencies/install-db2.yaml

### Dependency Management
- Install AMQStreams - dependencies/install-amqstreams.yaml
- Install Behavior Analytics Service - bas/install-bas.yaml
- Install MongoDb CE - dependencies/install-mongodb-ce.yaml
- Install IBM Suite License Service - sls/install-sls.yaml

### MAS Management
- Configure Application - mas/configure-app.yaml
- Configure MAS Core - mas/configure-suite.yaml
- Manage Db2 Database Configuration Hack - mas/hack-manage-db2.yaml
- Install Application - mas/install-app.yaml
- Install MAS Core - mas/install-suite.yaml

### OCP Management
- Configure OCP Cluster - ocp/configure-ocp.yaml


## Install Pipeline Operator
You can use the install script provided: `bin/install-pipelines.sh`, or just create the subscription below:

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
    name: openshift-pipelines-operator
    namespace: openshift-operators
spec:
    channel: stable
    name: openshift-pipelines-operator-rh
    source: redhat-operators
    sourceNamespace: openshift-marketplace
```


# Build and Install the MAS Pipeline Task Definitions
```
export DEV_MODE=true
export VERSION=5.1.0
pipelines/bin/build-pipelines.sh

cd pipelines
oc apply -f ibm-mas_devops-clustertasks-5.1.0.yaml
```


# Install and run the MAS Sample Pipeline
Modify the `samples/sample-pipelinesettings.yaml` file to populate it with your own settings before applying it to the cluster

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

# IBM Maximo Application Suite Tekton Pipelines

These pipelines are all powered by the container image in this same repository, and provide an alternative to running our Ansible roles and playbooks locally.  With Pipelines you can configure your own devops processes directly in the cluster and chain togther the building blocks (ClusterTasks) that we have created:

## ClusterTasks

### Cluster Management
- Configure OCP Cluster

### Dependency Management
- Install Db2 Warehouse
- Install AMQStreams
- Install MongoDb CE
- Install IBM Suite License Service

### MAS Management
- Configure Application
- Configure MAS Core
- Install Application
- Install MAS Core
- Manage Db2 Database Configuration Hack


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


# Install the MAS Pipeline Task Definitions
```
oc apply -f ibm.mas_devops.pipelines-x.y.z.yaml
```


# Install and run the MAS Sample Pipeline
```
oc apply -f samples/sample-pipeline.yaml
oc create -f samples/sample-pipelinerun.yaml
```

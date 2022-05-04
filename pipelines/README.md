# IBM Maximo Application Suite Tekton Pipelines

These pipelines are all powered by the container image in this same repository, and provide an alternative to running our Ansible roles and playbooks locally.  With Pipelines you can configure your own devops processes directly in the cluster and chain togther the building blocks (ClusterTasks) that we have created.

To learn more about Tekton refer to the excellent material here: https://redhat-scholars.github.io/tekton-tutorial/tekton-tutorial/index.html

This aspect of the project is still in active development and should be considered pre-release.  However, we are using these extensively in our own development, so they should be pretty reliable given we use them multiple times every day in our automation frameworks.

## ClusterTasks

# CP4D Management
- [Create Db2 Warehouse Instance](tasks/cp4d/create-db2-instance.yaml)
- [Install CP4D with Db2 Warehouse service enabled](tasks/cp4d/install-services-db2.yaml)
- [Install CP4D with Db2 Warehouse & Watson Studio services enabled](tasks/cp4d/install-services-fullstack.yaml)
- [Install CP4D with Watson Studio services enabled](tasks/cp4d/install-services-watsonstudio.yaml)

### Dependency Management
- [Install AMQStreams](tasks/dependencies/install-amqstreams.yaml)
- [Install Behavior Analytics Service (aka UDS)](tasks/dependencies/install-uds.yaml)
- [Install MongoDb CE](tasks/dependencies/install-mongodb-ce.yaml)
- [Install IBM Suite License Service](tasks/dependencies/install-sls.yaml)

### MAS Management
- [Configure Application](tasks/mas/configure-app.yaml)
- [Configure MAS Core](tasks/mas/configure-suite.yaml)
- [Manage Db2 Database Configuration Hack](tasks/mas/hack-manage-db2.yaml)
- [Install Application](tasks/mas/install-app.yaml)
- [Install MAS Core](tasks/mas/install-suite.yaml)
- [Run mustgather](tasks/mas/mustgather.yaml)
- [Generate Workspace config](tasks/mas/gencfg-workspace.yaml)

### OCP Management
- [Configure OCP Cluster for MAS](tasks/ocp/configure-ocp.yaml)


## Build and Install the MAS Pipeline Task Definitions
```bash
export DEV_MODE=true
export VERSION=10.0.0

pipelines/bin/build-pipelines.sh
oc apply -f pipelines/ibm-mas_devops-clustertasks-$VERSION.yaml
```

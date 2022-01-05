# Development Guide

## 1. Provision Cluster and Install OpenShift Pipelines Operator
Provision the cluster and perform the CP4D worker node hack (technically only required for CP4D v4):

```bash
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
ansible-playbook ibm/mas_devops/playbooks/ocp/provision-roks.yml && ansible-playbook ibm/mas_devops/playbooks/cp4d/hack-worker-nodes.yml
```

### 2. Install Pipelines feature
Sooner rather than later (and ahead of public release of the Tekton pipelines), we will fold this into the OCP provisioning role so that clusters have this capability "out of the box".

```bash
bash pipelines/bin/install-pipelines.sh
```

### 3. Set up the Pipeline Namespace
First, make a copy of `pipelines/samples/sample-pipelinesettings-roks.yaml` and set the real values as appropriate.  If you name it `pipelines/samples/sample-pipelinesettings-roks-donotcommit.yaml` then it will already be in the gitignore file.

```bash
oc new-project mas-sample-pipelines
oc apply -f pipelines/samples/sample-pipelinesettings-roks-donotcommit.yaml

oc create secret generic pipeline-additional-configs --from-file=/home/david/masconfig/workspace_masdev.yaml
oc create secret generic pipeline-sls-entitlement --from-file=/home/david/masconfig/entitlement.lic
```


### 4. Development Loop
Each time you want to modify and test a pipeline run, use the following:

```bash
export DEV_MODE=true
export VERSION=5.1.3

# Update the settings secret (if you changed any global settings)
oc apply -f pipelines/samples/sample-pipelinesettings-roks-donotcommit.yaml

# Build and update the clustertasks (if you changed any task definitions)
bash pipelines/bin/build-pipelines.sh && oc apply -f pipelines/ibm-mas_devops-clustertasks-$VERSION.yaml

# Update the pipeline definition and start a new run
oc apply -f pipelines/samples/sample-pipeline.yaml && oc create -f pipelines/samples/sample-pipelinerun-dev.yaml
```

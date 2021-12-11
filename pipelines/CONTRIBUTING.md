## Development


### Build new container image
```bash
export VERSION=4.5.1-pre.branch
cp ibm/mas_devops/ibm-mas_devops-$VERSION.tar.gz image/ansible-devops/ibm-mas_devops.tar.gz
docker build -t quay.io/ibmmas/ansible-devops:$VERSION image/ansible-devops
docker push quay.io/ibmmas/ansible-devops:$VERSION
```


### Build new tekton images
```bash
export DEV_MODE=true
export VERSION=4.5.1-pre.branch
bash pipelines/bin/build-pipelines.sh
```

### Install Pipelines feature & ClusterTask definitions
```bash
bash pipelines/bin/install-pipelines.sh
# Wait until the pipelines operator is installed
oc apply -f pipelines/ibm-mas_devops-clustertasks-$VERSION.yaml
```

### Install and run sample pipeline
First, make a copy of `pipelines/samples/sample-pipelinesettings-roks.yaml` and set the real values as appropriate.  If you name it `pipelines/samples/sample-pipelinesettings-roks-donotcommit.yaml` then it will already be in the gitignore file

```bash
oc new-project mas-sample-pipelines
oc apply -f pipelines/samples/sample-pipelinesettings-roks-donotcommit.yaml

oc create secret generic pipeline-additional-configs --from-file=/home/david/masconfig/workspace_masdev.yaml
oc create secret generic pipeline-sls-entitlement --from-file=/home/david/masconfig/entitlement.lic

oc apply -f pipelines/samples/sample-pipeline.yaml
oc create -f pipelines/samples/sample-pipelinerun.yaml
```


### Rebuild
Each time you want to modify and retry a pipeline run, use the following:

```bash
bash pipelines/bin/build-pipelines.sh
oc apply -f pipelines/ibm-mas_devops-clustertasks-$VERSION.yaml
oc apply -f pipelines/samples/sample-pipeline.yaml
oc create -f pipelines/samples/sample-pipelinerun.yaml
```
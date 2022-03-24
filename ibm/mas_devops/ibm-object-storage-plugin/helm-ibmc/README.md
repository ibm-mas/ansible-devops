## helm-ibmc

A Helm plugin that installs or upgrades Helm charts in IBM K8S Service

* https://docs.helm.sh/helm/#helm-ibmc

## Fixes
  * With v2.0.7, `ibmc` helm plugin has fix for installing chart in kube-system ns, if bucketAccessPolicy is set to true.
  This is because, to enable access policy for buckets, plugin needs access to `cluster-info` config-map which lies in kube-system ns.
  * With v2.0.6, `ibmc` helm plugin supports installation of object-storage-plugin on ibm-object-s3fs custom namespace.

## Installation
  * `helm repo add ibm-helm https://raw.githubusercontent.com/IBM/charts/master/repo/ibm-helm`
  * `helm repo update`
  * `helm fetch --untar ibm-helm/ibm-object-storage-plugin && cd ibm-object-storage-plugin`
  * `helm plugin install ./ibm-object-storage-plugin/helm-ibmc`
  * `helm ibmc --help`

## Upgrade
  * `helm ibmc --update`

## Usage

### Install IBM Cloud Object Storage plug-in chart(with helm client v3.x)
  * `helm ibmc install <release name> <chart repo>/<chart name> [flags]`
  * `helm ibmc install ibm-object-storage-plugin ibm-helm/ibm-object-storage-plugin --set license=true`

### Example
```
$ helm plugin install ./ibm-object-storage-plugin/helm-ibmc
Installed plugin: ibmc
$ helm ibmc --help
Helm version: v3.0.2+g19e47ee
Install or upgrade Helm charts in IBM K8S Service(IKS) and Red Hat OpenShift on IBM Cloud

Usage:
  helm ibmc [command]

Available Commands:
  install           Install a Helm chart
  upgrade           Upgrade the release to a new version of the Helm chart

Available Flags:
  -h, --help        (Optional) This text.
  -u, --update      (Optional) Update this plugin to the latest version

Example Usage:
    Install: helm ibmc install ibm-object-storage-plugin ibm-charts/ibm-object-storage-plugin
    Upgrade: helm ibmc upgrade [RELEASE] ibm-charts/ibm-object-storage-plugin

Note:
    1. It is always recommended to install latest version of ibm-object-storage-plugin chart.
    2. It is always recommended to have 'kubectl' client up-to-date.
```

```
$ helm ibmc install ibm-object-storage-plugin ./ --set license=true --set bucketAccessPolicy=true
v3.6.3+gd506314
Checking cluster type
Fetching WORKER OS details ...
Installing the Helm chart...
PROVIDER: IBMC-VPC
WORKER_OS: redhat
PLATFORM: openshift
KUBE_DRIVER_PATH: /usr/libexec/kubernetes
CONFIG_BUCKET_ACCESS_POLICY: true
DC: dal10
Region: us-south
Chart: ./
NAME: ibm-object-storage-plugin
LAST DEPLOYED: Tue Aug 31 19:43:05 2021
NAMESPACE: kube-system
STATUS: deployed
REVISION: 1
NOTES:
Thank you for installing: ibm-object-storage-plugin.   Your release is named: ibm-object-storage-plugin

1. Verify that the storage classes are created successfully:

   $ oc get storageclass | grep 'ibmc-s3fs'

2. Verify that plugin pods are in "Running" state:

   $ oc get pods -n kube-system -o wide | grep object

   The installation is successful when you see one `ibmcloud-object-storage-plugin` pod and one or more `ibmcloud-object-storage-driver` pods.
   The number of `ibmcloud-object-storage-driver` pods equals the number of worker nodes in your cluster. All pods must be in a `Running` state
   for the plug-in to function properly. If the pods fail, run `oc describe pod -n kube-system <pod_name>`
   to find the root cause for the failure.
######################################################
Additional steps for IBM Kubernetes Service(IKS) only:
######################################################

  1. If the plugin pods show an "ErrImagePull" or "ImagePullBackOff" error, copy the image pull secret 'all-icr-io' from "default" namespace to kube-system namespace of your cluster. The image pull secret 'all-icr-io' provides access to IBM Cloud Container Registry.

     a. Check the secret exists in "default" namespace

     $ oc get secrets -n default | grep icr-io

     Example output:
     ------------------------------------------------------------------
     all-icr-io         kubernetes.io/dockerconfigjson        1      2d
     ------------------------------------------------------------------

     b. Copy secret to kube-system  namespace

     $ kubectl get secret -n default all-icr-io -o yaml | sed 's/default/<namespace>/g' | kubectl -n <namespace> create -f -

     c. Verify that the image pull secret is available in the kube-system  namespace.

     $ oc get secrets -n kube-system | grep icr-io

  2. Verify that the state of the plugin pods changes to "Running".

     $ oc get pods -n kube-system | grep object

```

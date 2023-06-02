OneClick Update
===============================================================================
This playbook will **update** the IBM Maximo Operator Catalog on your OpenShift cluster.  This will make available new operator updates, which will be automatically applied across the cluster.  These updates will not change the functionality of the software in your cluster, they will only carry fixes for security vulnerabilities and bugs.

!!! note
    If you are using the dynamic catalog (**ibm-maximo-operator-catalog:v8**) this playbook can be ignored, as you will recieve catalog updates in your cluster as soon as they are released.  This playbook is specifically for customers who choose to use static catalogs to control the consumption of updates in their cluster.

This is distinct from an **upgrade**, which will modify the operator subscriptions on your cluster to deliver new features.  Performing an updating may make new upgrades available in the cluster, but it will **never** initiate the upgrade, you must choose when to upgrade.


Playbook Content
-------------------------------------------------------------------------------
1. [Install IBM Operator Catalog](../roles/ibm_catalogs.md) (1 minute)


Preparation
-------------------------------------------------------------------------------
You will need to determine the version of the IBM Maximo Operator Catalog that you wish to update to.  Generally speaking, you should update the most recent catalog available.  The following catalogs are available at time of writing:

- **v8-220805-amd64**
- **v8-220717-amd64**

!!! important
    If you are using a private/mirror registry it is **critical** that you mirror the images from the updated catalog **before** you run this playbook, otherwise you will see numerous containers in **ImagePullBackoff** as the updates are rolled out automatically after the catalog has been updated.

    You do not need to worry about translating the image tags to digests to make these catalogs compatible with image mirroring on OpenShift, the role will automatically usse the image digest when it installs any static operator catalog.


Usage
-------------------------------------------------------------------------------
### Required environment variables
- `MAS_CATALOG_VERSION`

### Example
Only one parameter is required, the new tag of the IBM Maximo Operator Catalog that you wish to use:

```bash
export MAS_CATALOG_VERSION=v8-230526-amd64
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_update
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the update from inside our container image: `docker run -ti --rm --pull always quay.io/ibmmas/cli`

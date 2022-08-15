OneClick Upgrade
===============================================================================
This playbook will **upgrade** the channel subscriptions for IBM Maximo Application Suite on your OpenShift cluster.  Upgrades can only be performed to releases available in the  version of the IBM Maximo Pperator Catalog that is installed in your cluster.  To **update** to a newer version of the operator catalog refer to the [oneclick-update.md](oneclick-update) playbook documentation.

The playbook will attempt to upgrade MAS Core and all installed applications.

!!! note
    If you are using the dynamic catalog (**ibm-maximo-operator-catalog:v8**) you will always have access to the latest MAS releases, as you will recieve catalog updates in your cluster as soon as they are released.  Customers using the static catalogs to control the consumption of updates in their cluster will need to ensure that the version of the catalog they have installed supports the version of MAS that they wish to upgrade to.


Playbook Content
-------------------------------------------------------------------------------
1. [Upgrade MAS Core](../roles/suite_upgrade.md)
1. [Verify MAS Core](../roles/suite_verify.md)
2. [Upgrade MAS Application (Assist)](../roles/suite_app_upgrade.md)
3. [Upgrade MAS Application (HP Utilities)](../roles/suite_app_upgrade.md)
4. [Upgrade MAS Application (IoT)](../roles/suite_app_upgrade.md)
5. [Upgrade MAS Application (Manage)](../roles/suite_app_upgrade.md)
6. [Upgrade MAS Application (Monitor)](../roles/suite_app_upgrade.md)
7. [Upgrade MAS Application (Optimizer)](../roles/suite_app_upgrade.md)
8. [Upgrade MAS Application (Predict)](../roles/suite_app_upgrade.md)
9. [Upgrade MAS Application (Safety)](../roles/suite_app_upgrade.md)
10. [Upgrade MAS Application (Visual Inspection)](../roles/suite_app_upgrade.md)


Preparation
-------------------------------------------------------------------------------
If you are using a private/mirror registry it is **critical** that you mirror the images for the new release **before** you run this playbook, otherwise you will see numerous containers in **ImagePullBackoff** as the updates are rolled out automatically after the subscription has been changed, if you have not mirrored the new images the subscription change itself may fail if the operator bundle is not on your private registry.


Usage
-------------------------------------------------------------------------------
### Required Parameters
- `MAS_INSTANCE_ID` Set the instance ID of the MAS installation to upgrade

### Optional Parameters
If you provide no values for MAS Core or the individual applications, the roles will attempt to upgrade to the next level of MAS and upgrade applications to the latest version supported by the installed version of MAS Core (after upgrading MAS Core).

- `MAS_CHANNEL` Set the target subscription channel for MAS Core
- `MAS_APP_CHANNEL_ASSIST` Set the target subscription channel for Assist
- `MAS_APP_CHANNEL_HPUTILITIES` Set the target subscription channel for Health & Predict Utilities
- `MAS_APP_CHANNEL_IOT` Set the target subscription channel for IoT
- `MAS_APP_CHANNEL_MONITOR` Set the target subscription channel for Monitor
- `MAS_APP_CHANNEL_OPTIMIZER` Set the target subscription channel for Optimizer
- `MAS_APP_CHANNEL_PREDICT` Set the target subscription channel for Predict
- `MAS_APP_CHANNEL_SAFETY` Set the target subscription channel for Safety
- `MAS_APP_CHANNEL_VISUALINSPECTION` Set the target subscription channel for Visual Inspection

### Example
The simplest way to upgrade MAS is to provide only the instance ID that you wish to upgrade, allowing the roles to determine the correct target version each application.

```bash
export MAS_INSTANCE_ID=instance1
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_upgrade
```

You can also explicitly specify the target upgrade:

```bash
export MAS_INSTANCE_ID=instance1
export MAS_CHANNEL=8.8.x
export MAS_APP_CHANNEL_IOT=8.5.x
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_upgrade
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the update from inside our container image: `docker run -ti --rm quay.io/ibmmas/cli:latest`

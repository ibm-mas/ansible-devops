nvidia_gpu
==========

This role installs the **NVIDIA Graphical Processing Unit (GPU)** operator and its prerequisite **Node Feature Discovery (NFD)** operator in an IBM Cloud Openshift cluster console. The role first installs the NFD operator and continues with the final step to install the NVIDIA GPU Operator. The NFD Operator is installed using the Red Hat Operators catalog source and the GPU operator is installed using the Certified Operators catalog source.


Role Variables
--------------

### nfd_namespace
The namespace where the node feature discovery operator will be deployed.

- Environment Variable: `NFD_NAMESPACE`
- Default Value: `openshift-nfd`

### nfd_channel
The channel to subscribe to for the nfd operator installation and updates. Available channels may be found in the package manifest of nfd operator in openshift.

- Environment Variable: `NFD_CHANNEL`
- Default Value: `stable`

### gpu_namespace
The namespace where the NVIDIA GPU operator will be deployed. For version 1.8.x, use of single namespace is not supported, therefore use `openshift-operators`.

- Environment Variable: `GPU_NAMESPACE`
- Default Value: `nvidia-gpu-operator`

### gpu_channel
The channel to subscribe to for the gpu operator installation and updates. Available channels may be found in the package manifest of gpu-operator-certified operator in openshift.

- Environment Variable: `GPU_CHANNEL`
- Default Value: `v23.3`

### gpu_driver_version
The gpu driver version image that needs to be pulled from the gpu driver repository. It is recommended that the right version of GPU driver is used depending on the OS version. The default versions are shown below. See the attached links for more information and to decide which driver version to use.

- Environment Variable: `GPU_DRIVER_VERSION`
- Default Value: `470.182.03` if ocp version 4.10+ and `450.80.02` otherwise
The deciding factor for which image version to use is the RHEL or RHCOS version.
RHEL 8.6            ---> 470.182.03
RHEL 7.9            ---> 450.80.02
The version of RHEL that is used by OCP version is per https://cloud.ibm.com/docs/openshift?topic=openshift-rhel_migrate

OCP 4.10+           ---> RHEL 8
OCP 4.9             ---> Either RHEL 8 or RHEL 7 with 7 being the default
OCP 4.6, 4.7, & 4.8 ---> RHEL 7

RHCOS 4.9 & 4.0     ---> 470.182.03
RHCOS 4.4 - 4.6     ---> 450.80.02
For other RHCOS versions find an appropriate driver version at https://catalog.ngc.nvidia.com/orgs/nvidia/containers/driver/tags

### gpu_driver_repository_path
The gpu driver repository. If using a different repository, you can set the value for this repo. We only support public repositories at the moment.

- Environment Variable: `GPU_DRIVER_REPOSITORY_PATH`
- Default Value: `nvcr.io/nvidia`

For more information on the NVIDIA GPU and NFD operators, visit https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-gpu-ocp.html



Example Playbook
----------------


```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.nvidia_gpu
```


License
-------

EPL-2.0

nvidia_gpu
==========

This role installs the **NVIDIA Graphical Processing Unit (GPU)** operator and its prerequisite **Node Feature Discovery (NFD)** operator in an IBM Cloud Openshift cluster console. The role first installs the NFD operator and continues with the final step to install the NVIDIA GPU Operator. The NFD Operator is installed using the Red Hat Operators catalog source and the GPU operator is installed using the Certified Operators catalog source.


Role Variables
--------------

### nfd_namespace
The namespace where the node feature discovery operator will be deployed.

- Environment Variable: `NFD_NAMESPACE`
- Default Value: `gpu-operator-resources`

### nfd_channel
The channel to subscribe to for the nfd operator installation and updates. Available channels may be found in the package manifest of nfd operator in openshift.

- Environment Variable: `NFD_CHANNEL`
- Default Value: `stable`

### gpu_namespace
The namespace where the NVIDIA GPU operator will be deployed. For version 1.8.x, use of single namespace is not supported, therefore namespace is defaulted to `openshift-operators`. NVIDIA's suggested namespace to use for versions 1.9.0 and above is `nvidia-gpu-operator`

- Environment Variable: `GPU_NAMESPACE`
- Default Value: `openshift-operators`

### gpu_channel
The channel to subscribe to for the gpu operator installation and updates. Available channels may be found in the package manifest of gpu-operator-certified operator in openshift.

- Environment Variable: `GPU_CHANNEL`
- Default Value: `v1.8`

### gpu_driver_version
The gpu driver version image that needs to be pulled from the gpu repository. It is recommended that the right version if GPU driver is used. The MVI installation documentation, the default version below should be used.

- Environment Variable: `GPU_DRIVER_VERSION`
- Default Value: `450.80.02`



For more information on the NVIDIA GPU and NFD operators, visit https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-gpu-ocp.html



Example Playbook
----------------


```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.gpu_install
```


License
-------

EPL-2.0

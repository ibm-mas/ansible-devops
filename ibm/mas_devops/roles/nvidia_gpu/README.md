# nvidia_gpu
This role installs and configures the NVIDIA GPU Operator on OpenShift clusters to enable GPU workloads. The GPU Operator manages the lifecycle of NVIDIA software components required to run GPU-accelerated applications.

The role automatically installs the Node Feature Discovery (NFD) Operator as a prerequisite, then deploys the NVIDIA GPU Operator and creates a ClusterPolicy to configure GPU support across the cluster. This is required for applications like Maximo Visual Inspection that need GPU acceleration.

## Prerequisites
- OpenShift cluster with GPU-enabled worker nodes
- Cluster administrator access
- GPU-capable hardware (NVIDIA GPUs) available in the cluster

## Role Variables

### GPU Operator Variables

#### gpu_namespace
The namespace where the NVIDIA GPU Operator will be installed.

- **Optional**
- Environment Variable: `GPU_NAMESPACE`
- Default Value: `nvidia-gpu-operator`

#### gpu_channel
The subscription channel for the GPU Operator. This determines which version of the operator will be installed.

- **Optional**
- Environment Variable: `GPU_CHANNEL`
- Default Value: `v24.9`

#### gpu_driver_version
Specific NVIDIA driver version to install. If not specified, the latest compatible driver version will be used.

- **Optional**
- Environment Variable: `GPU_DRIVER_VERSION`
- Default Value: None (uses latest)

#### gpu_driver_repository_path
The container registry path for NVIDIA driver images.

- **Optional**
- Environment Variable: `GPU_DRIVER_REPOSITORY_PATH`
- Default Value: `nvcr.io/nvidia`

### Node Feature Discovery Variables

#### nfd_namespace
The namespace where the Node Feature Discovery Operator will be installed. NFD is required by the GPU Operator to detect GPU hardware.

- **Optional**
- Environment Variable: `NFD_NAMESPACE`
- Default Value: `openshift-nfd`

#### nfd_channel
The subscription channel for the Node Feature Discovery Operator.

- **Optional**
- Environment Variable: `NFD_CHANNEL`
- Default Value: `stable`

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    gpu_namespace: nvidia-gpu-operator
    gpu_channel: v24.9
    nfd_namespace: openshift-nfd
  roles:
    - ibm.mas_devops.nvidia_gpu
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export GPU_NAMESPACE=nvidia-gpu-operator
export GPU_CHANNEL=v24.9
export NFD_NAMESPACE=openshift-nfd
ROLE_NAME=nvidia_gpu ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0

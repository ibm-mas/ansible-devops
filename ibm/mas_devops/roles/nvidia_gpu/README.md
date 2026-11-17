# nvidia_gpu
This role installs and configures the NVIDIA GPU Operator on OpenShift clusters to enable GPU workloads. The GPU Operator manages the lifecycle of NVIDIA software components required to run GPU-accelerated applications.

The role automatically installs the Node Feature Discovery (NFD) Operator as a prerequisite, then deploys the NVIDIA GPU Operator and creates a ClusterPolicy to configure GPU support across the cluster. This is required for applications like Maximo Visual Inspection that need GPU acceleration.

## Prerequisites

- OpenShift cluster with GPU-enabled worker nodes
- Cluster administrator access
- GPU-capable hardware (NVIDIA GPUs) available in the cluster

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`gpu_namespace`](#gpu_namespace) | No | `nvidia-gpu-operator` |
| [`gpu_channel`](#gpu_channel) | No | `v26.3` (OCP >= 4.21) / `v25.3` (OCP < 4.21) |
| [`gpu_driver_version`](#gpu_driver_version) | No | None |
| [`gpu_driver_repository_path`](#gpu_driver_repository_path) | No | `nvcr.io/nvidia` |
| [`nfd_namespace`](#nfd_namespace) | No | `openshift-nfd` |
| [`nfd_channel`](#nfd_channel) | No | `stable` |

### GPU Operator Variables

#### gpu_namespace
OpenShift namespace where the NVIDIA GPU Operator and its components (deployments, services, ClusterPolicy) are deployed — a valid Kubernetes namespace name (lowercase alphanumeric with hyphens).

- **Optional**
- Environment Variable: `GPU_NAMESPACE`
- Default: `nvidia-gpu-operator`

The namespace is created if it doesn't exist, and the GPU Operator manages cluster-wide GPU resources regardless of namespace. The default is recommended for most deployments; override only for specific namespace requirements or multiple GPU operator instances.

#### gpu_channel
NVIDIA GPU Operator subscription channel, determining which version stream is installed from OperatorHub — for example `v26.3`, `v25.3`, `v24.9`, or `v24.6`.

- **Optional**
- Environment Variable: `GPU_CHANNEL`
- Default: `v26.3` for OpenShift >= 4.21, `v25.3` for OpenShift < 4.21 (auto-detected from the cluster's OpenShift version)

Newer channels provide the latest features and driver support but may require newer OpenShift versions. Check the [NVIDIA GPU Operator platform support matrix](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/platform-support.html) for compatibility, and set a channel explicitly only to pin to a specific version.

#### gpu_driver_version
Specific NVIDIA GPU driver version to install — a valid NVIDIA driver version string such as `535.129.03` or `550.54.15` — instead of the latest version provided by the operator channel.

- **Optional**
- Environment Variable: `GPU_DRIVER_VERSION`
- Default: None (uses latest compatible version)

Specify only when you need a particular driver version for compatibility, stability, or certification requirements; the latest driver is usually recommended otherwise. Verify compatibility with your GPU hardware via the [NVIDIA driver compatibility matrix](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/platform-support.html), and ensure the version is available in the specified repository.

#### gpu_driver_repository_path
Container registry path where NVIDIA GPU driver container images are stored — a valid registry path such as `nvcr.io/nvidia` or `registry.example.com/nvidia-drivers`.

- **Optional**
- Environment Variable: `GPU_DRIVER_REPOSITORY_PATH`
- Default: `nvcr.io/nvidia`

The GPU Operator pulls driver container images from this registry location. Override for air-gapped environments using a mirrored registry (mirror the images to an internal registry accessible from the cluster); private registries may require image pull secrets.

### Node Feature Discovery Variables

#### nfd_namespace
OpenShift namespace where the Node Feature Discovery (NFD) Operator is deployed — a valid Kubernetes namespace name (lowercase alphanumeric with hyphens). NFD detects GPU hardware and labels nodes with hardware features for the GPU Operator to use.

- **Optional**
- Environment Variable: `NFD_NAMESPACE`
- Default: `openshift-nfd`

NFD is automatically installed by this role as a prerequisite for the GPU Operator and must be installed before it. The namespace is created if it doesn't exist; the default `openshift-nfd` is the standard namespace for NFD.

#### nfd_channel
Node Feature Discovery Operator subscription channel, determining which version stream is installed from OperatorHub — typically `stable`, with version-specific channels possibly available.

- **Optional**
- Environment Variable: `NFD_CHANNEL`
- Default: `stable`

The `stable` channel provides production-ready releases and is recommended for production. Check OperatorHub for available channels in your OpenShift version; the NFD version should be compatible with the OpenShift version.

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    gpu_namespace: nvidia-gpu-operator
    gpu_channel: v26.3
    nfd_namespace: openshift-nfd
  roles:
    - ibm.mas_devops.nvidia_gpu
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export GPU_NAMESPACE=nvidia-gpu-operator
export GPU_CHANNEL=v26.3
export NFD_NAMESPACE=openshift-nfd
ROLE_NAME=nvidia_gpu ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0

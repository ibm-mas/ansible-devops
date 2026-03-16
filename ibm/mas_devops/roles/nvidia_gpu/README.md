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
Namespace for NVIDIA GPU Operator installation.

- **Optional**
- Environment Variable: `GPU_NAMESPACE`
- Default: `nvidia-gpu-operator`

**Purpose**: Specifies the OpenShift namespace where the NVIDIA GPU Operator and its components will be deployed.

**When to use**: Use default unless you have specific namespace requirements or multiple GPU operator instances.

**Valid values**: Valid Kubernetes namespace name (lowercase alphanumeric with hyphens)

**Impact**: All GPU Operator resources (deployments, services, ClusterPolicy) will be created in this namespace.

**Related variables**: [`nfd_namespace`](#nfd_namespace)

**Notes**:
- Default namespace is recommended for most deployments
- Namespace will be created if it doesn't exist
- GPU Operator manages cluster-wide GPU resources regardless of namespace

#### gpu_channel
NVIDIA GPU Operator subscription channel.

- **Optional**
- Environment Variable: `GPU_CHANNEL`
- Default: `v24.9`

**Purpose**: Determines which version stream of the NVIDIA GPU Operator will be installed from OperatorHub.

**When to use**: Use default for latest stable version. Specify older channel for compatibility with specific OpenShift versions or when stability is prioritized over features.

**Valid values**: Valid GPU Operator channel versions (e.g., `v24.9`, `v24.6`, `v23.9`)

**Impact**: Controls which operator version is installed and which features are available. Newer channels may require newer OpenShift versions.

**Related variables**: [`gpu_driver_version`](#gpu_driver_version)

**Notes**:
- Check [NVIDIA GPU Operator releases](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/platform-support.html) for compatibility
- Newer channels provide latest features and driver support
- Consider OpenShift version compatibility when selecting channel

#### gpu_driver_version
Specific NVIDIA GPU driver version to install.

- **Optional**
- Environment Variable: `GPU_DRIVER_VERSION`
- Default: None (uses latest compatible version)

**Purpose**: Pins the NVIDIA GPU driver to a specific version instead of using the latest version provided by the operator channel.

**When to use**: Specify when you need a particular driver version for compatibility, stability, or certification requirements. Leave unset to use the latest compatible driver.

**Valid values**: Valid NVIDIA driver version string (e.g., `535.129.03`, `550.54.15`)

**Impact**: When set, the specified driver version will be installed. When unset, the operator installs the latest driver compatible with the operator channel.

**Related variables**: [`gpu_channel`](#gpu_channel), [`gpu_driver_repository_path`](#gpu_driver_repository_path)

**Notes**:
- Latest driver is usually recommended unless specific version is required
- Verify driver compatibility with your GPU hardware
- Check [NVIDIA driver compatibility matrix](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/platform-support.html)
- Driver version must be available in the specified repository

#### gpu_driver_repository_path
Container registry path for NVIDIA driver images.

- **Optional**
- Environment Variable: `GPU_DRIVER_REPOSITORY_PATH`
- Default: `nvcr.io/nvidia`

**Purpose**: Specifies the container registry location where NVIDIA GPU driver container images are stored.

**When to use**: Use default for public NVIDIA registry. Override for air-gapped environments or when using a mirrored registry.

**Valid values**: Valid container registry path (e.g., `nvcr.io/nvidia`, `registry.example.com/nvidia-drivers`)

**Impact**: GPU Operator will pull driver container images from this registry location.

**Related variables**: [`gpu_driver_version`](#gpu_driver_version)

**Notes**:
- Default points to NVIDIA's official registry
- For air-gapped deployments, mirror images to internal registry
- Ensure registry is accessible from OpenShift cluster
- May require image pull secrets for private registries

### Node Feature Discovery Variables

#### nfd_namespace
Namespace for Node Feature Discovery Operator installation.

- **Optional**
- Environment Variable: `NFD_NAMESPACE`
- Default: `openshift-nfd`

**Purpose**: Specifies the OpenShift namespace where the Node Feature Discovery (NFD) Operator will be deployed. NFD is a prerequisite for GPU Operator.

**When to use**: Use default unless you have specific namespace requirements. NFD must be installed before GPU Operator.

**Valid values**: Valid Kubernetes namespace name (lowercase alphanumeric with hyphens)

**Impact**: NFD Operator resources will be created in this namespace. NFD detects GPU hardware and labels nodes accordingly.

**Related variables**: [`gpu_namespace`](#gpu_namespace), [`nfd_channel`](#nfd_channel)

**Notes**:
- NFD is automatically installed by this role as a prerequisite
- Default `openshift-nfd` is the standard namespace for NFD
- NFD labels nodes with hardware features for GPU Operator to use
- Namespace will be created if it doesn't exist

#### nfd_channel
Node Feature Discovery Operator subscription channel.

- **Optional**
- Environment Variable: `NFD_CHANNEL`
- Default: `stable`

**Purpose**: Determines which version stream of the Node Feature Discovery Operator will be installed from OperatorHub.

**When to use**: Use default `stable` for production deployments. Other channels may be available for testing or specific versions.

**Valid values**: Valid NFD Operator channel (typically `stable`, may include version-specific channels)

**Impact**: Controls which NFD operator version is installed. The `stable` channel provides production-ready releases.

**Related variables**: [`nfd_namespace`](#nfd_namespace), [`gpu_channel`](#gpu_channel)

**Notes**:
- `stable` channel is recommended for production
- NFD is a prerequisite for GPU Operator functionality
- Check OperatorHub for available channels in your OpenShift version
- NFD version should be compatible with OpenShift version

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

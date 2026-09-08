# Ansible DevOps: Kafka Image Processor PVC Support

## Objective
Add support in the `suite_app_config` role for configuring Kafka Image Processor PVC settings that will be passed to the ManageWorkspace CR's `spec.components.civil.persistentVolumeClaims.kafkaImageProcessor` field.

## Critical Rules
- Use consistent environment variable naming: `MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_SIZE` and `MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_STORAGECLASS`
- Follow existing PVC configuration patterns (JMS, doclinks, BIM)
- Storage class auto-detection must use same logic as other Manage PVCs (RWX)
- Only configure when civil component is enabled AND PVC variables are set
- Default size: 10Gi
- Access mode: ReadWriteMany (hardcoded in operator, not configurable here)

## Execution Plan

### Phase 1: Add Environment Variables and Defaults ✅

#### 1.1 Update `ibm/mas_devops/roles/suite_app_config/defaults/main.yml` ✅
Add after line 94 (after manage encryption secret variables):

```yaml
# Manage Kafka Image Processor PVC (Civil Component)
# -----------------------------------------------------------------------------
mas_manage_kafkaimageprocessor_pvc_storageclass: "{{ lookup('env', 'MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_STORAGECLASS') }}"
mas_manage_kafkaimageprocessor_pvc_size: "{{ lookup('env', 'MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_SIZE') | default('10Gi', true) }}"
```

### Phase 2: Update Storage Class Determination ✅

#### 2.1 Update `ibm/mas_devops/roles/suite_app_config/tasks/determine-storage-classes.yml` ✅

Add after line 35 (after JMS queue storage class):

```yaml
- name: "determine-storage-classes : Set kafka image processor default pvc storage class"
  when: mas_manage_kafkaimageprocessor_pvc_storageclass is not defined or mas_manage_kafkaimageprocessor_pvc_storageclass == ""
  set_fact:
    mas_manage_kafkaimageprocessor_pvc_storageclass: "{{ mas_app_settings_default_pvc_storage_class }}"
```

Update assertion section (after line 48) to include:

```yaml
- name: "determine-storage-classes : Assert Manage related storage classes are defined"
  assert:
    that:
      - mas_app_settings_doclinks_pvc_storage_class is defined
      - mas_app_settings_doclinks_pvc_storage_class != ''
      - mas_app_settings_bim_pvc_storage_class is defined
      - mas_app_settings_bim_pvc_storage_class != ''
      - mas_app_settings_jms_queue_pvc_storage_class is defined
      - mas_app_settings_jms_queue_pvc_storage_class != ''
      - mas_manage_kafkaimageprocessor_pvc_storageclass is defined
      - mas_manage_kafkaimageprocessor_pvc_storageclass != ''
    fail_msg:
      - "Failed: One of more storage classes are not defined for Manage"
      - ""
      - "Doclinks PVC Storage Class .............. {{ mas_app_settings_doclinks_pvc_storage_class | default('<undefined>', true) }}"
      - "BIM PVC Storage Class  .................. {{ mas_app_settings_bim_pvc_storage_class | default('<undefined>', true) }}"
      - "JMS Queue Storage Class ................. {{ mas_app_settings_jms_queue_pvc_storage_class | default('<undefined>', true) }}"
      - "Kafka Image Processor Storage Class .... {{ mas_manage_kafkaimageprocessor_pvc_storageclass | default('<undefined>', true) }}"
```

### Phase 3: Check Manage Version and Create Kafka Image Processor PVC Setup Task ✅

#### 3.1 Create `ibm/mas_devops/roles/suite_app_config/tasks/manage/pre-config/check-manage-version.yml` ✅

```yaml
---
# Check Manage application version to determine if Kafka Image Processor PVC is required
# ------------------------------------------------------------------------
- name: "Get ManageApp CR to check version"
  kubernetes.core.k8s_info:
    api_version: apps.mas.ibm.com/v1
    kind: ManageApp
    name: "{{ mas_instance_id }}"
    namespace: "mas-{{ mas_instance_id }}-manage"
  register: manage_app_info

- name: "Fail if ManageApp CR not found"
  assert:
    that:
      - manage_app_info.resources is defined
      - manage_app_info.resources | length > 0
    fail_msg: "ManageApp CR '{{ mas_instance_id }}' not found in namespace 'mas-{{ mas_instance_id }}-manage'. Cannot determine if Kafka Image Processor PVC configuration is required for Civil component."

- name: "Fail if ManageApp version information not available"
  assert:
    that:
      - manage_app_info.resources[0].status is defined
      - manage_app_info.resources[0].status.versions is defined
      - manage_app_info.resources[0].status.versions.reconciled is defined
    fail_msg: "ManageApp CR '{{ mas_instance_id }}' does not have version information in status.versions.reconciled. Cannot determine if Kafka Image Processor PVC configuration is required for Civil component."

- name: "Extract Manage version"
  set_fact:
    manage_reconciled_version: "{{ manage_app_info.resources[0].status.versions.reconciled }}"

- name: "Extract major.minor version from reconciled version"
  set_fact:
    manage_major_minor: "{{ manage_reconciled_version.split('.')[0] }}.{{ manage_reconciled_version.split('.')[1] }}"

- name: "Debug Manage version information"
  debug:
    msg:
      - "Manage reconciled version ............. {{ manage_reconciled_version }}"
      - "Manage major.minor version ............ {{ manage_major_minor }}"

- name: "Determine if Kafka Image Processor PVC is required (Manage >= 9.2)"
  when:
    - manage_major_minor is version('9.2', '>=')
  set_fact:
    manage_requires_kafka_image_processor_pvc: true

- name: "Set flag when Kafka Image Processor PVC is not required"
  when: manage_requires_kafka_image_processor_pvc is not defined
  set_fact:
    manage_requires_kafka_image_processor_pvc: false

- name: "Debug Kafka Image Processor PVC requirement"
  debug:
    msg: "Kafka Image Processor PVC required: {{ manage_requires_kafka_image_processor_pvc }}"
```

#### 3.2 Create `ibm/mas_devops/roles/suite_app_config/tasks/manage/pre-config/setup-kafka-image-processor-pvc.yml` ✅

```yaml
---
# Manage specific steps to configure Kafka Image Processor PVC for Civil component
# ------------------------------------------------------------------------
- name: "Debug Kafka Image Processor PVC configuration"
  debug:
    msg:
      - "Kafka Image Processor PVC Size ............ {{ mas_manage_kafkaimageprocessor_pvc_size }}"
      - "Kafka Image Processor PVC Storage Class ... {{ mas_manage_kafkaimageprocessor_pvc_storageclass }}"

- name: "Set Kafka Image Processor PVC configuration for civil component"
  set_fact:
    mas_manage_civil_kafka_image_processor_pvc:
      kafkaImageProcessor:
        size: "{{ mas_manage_kafkaimageprocessor_pvc_size }}"
        storageClassName: "{{ mas_manage_kafkaimageprocessor_pvc_storageclass }}"
```

#### 3.3 Update `ibm/mas_devops/roles/suite_app_config/tasks/manage/pre-config/main.yml` ✅

Add after line 51 (after encryption secret setup):

```yaml
# Manage pre-configuration: Check Manage version for Kafka Image Processor PVC requirement
- name: "Run Manage specific pre-configuration: Check Manage version"
  when:
    - manageWorkspaceComponents is defined
    - manageWorkspaceComponents.civil is defined
    - manageWorkspaceComponents.civil.version is defined
  include_tasks: "tasks/manage/pre-config/check-manage-version.yml"

# Manage pre-configuration: Kafka Image Processor PVC setup (Civil component)
- name: "Run Manage specific pre-configuration: Set up Kafka Image Processor PVC"
  when:
    - manageWorkspaceComponents is defined
    - manageWorkspaceComponents.civil is defined
    - manageWorkspaceComponents.civil.version is defined
    - manage_requires_kafka_image_processor_pvc is defined
    - manage_requires_kafka_image_processor_pvc | bool
  include_tasks: "tasks/manage/pre-config/setup-kafka-image-processor-pvc.yml"
```

### Phase 4: Update Component Template ✅

#### 4.1 Update `ibm/mas_devops/roles/suite_app_config/vars/customspecs/manage_components.yml.j2` ✅

Replace lines 96-102 (civil component section) with:

```jinja2
{% if manageWorkspaceComponents['civil'] is defined and manageWorkspaceComponents['civil']['version'] is defined %}
civil:
{% if ibm_mas_manage_imagestitching_pod_templates is defined %}
  podTemplates: {{ ibm_mas_manage_imagestitching_pod_templates }}
{% endif %}
{% if mas_manage_civil_kafka_image_processor_pvc is defined %}
  persistentVolumeClaims: {{ mas_manage_civil_kafka_image_processor_pvc }}
{% endif %}
  version: {{ manageWorkspaceComponents['civil']['version'] }}
{% endif %}
```

### Phase 5: Update Documentation ✅

#### 5.1 Add documentation in `ibm/mas_devops/roles/suite_app_config/README.md` ✅

Add new section after line 680 (after Doclinks/Attachments section, before BIM section):

```markdown
### Kafka Image Processor (Civil Component)

The following properties can be defined to configure the persistent volume for the Kafka Image Processor component when the Civil Infrastructure component is enabled.

**Important:** As of Manage 9.2, these properties are **required** when the Civil Infrastructure component is enabled. They are not supported in earlier releases. The role automatically detects the Manage version and only includes these settings when Manage >= 9.2.

#### mas_manage_kafkaimageprocessor_pvc_storageclass
Provide the persistent volume storage class to be used for Kafka Image Processor configuration. The PVC will be created with `ReadWriteMany` access mode as it must be shared between Manage/Civil and KafkaImageProcessor deployments.

- **Optional** (automatically included when Civil component is enabled in Manage 9.2+)
- Environment Variable: `MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_STORAGECLASS`
- Default: None - If not set, a default storage class will be auto-defined according to your cluster's available storage classes

#### mas_manage_kafkaimageprocessor_pvc_size
Provide the persistent volume claim size to be used for Kafka Image Processor configuration.

- **Optional** (automatically included when Civil component is enabled in Manage 9.2+)
- Environment Variable: `MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_SIZE`
- Default: `10Gi`
```

### Phase 6: Validation ✅

#### 6.1 Verify version detection logic ✅
- [x] Version detection correctly extracts major.minor from reconciled version using split()
- [x] Version comparison works with extended semver strings (e.g., "9.2.0-pre.feature+123")
- [x] Handles case when ManageApp CR doesn't exist or version not available (fails with clear error)

#### 6.2 Review all changes for consistency ✅
- [x] Variable naming follows consistent pattern (`MAS_MANAGE_*` not `MAS_APP_SETTINGS_*`)
- [x] Default values match requirements (10Gi)
- [x] Storage class logic matches other Manage PVCs
- [x] Conditional logic checks for civil component enablement AND version >= 9.2

#### 6.3 Verify variable naming conventions ✅
- [x] Environment variables use `MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_*` format
- [x] Internal variables use `mas_manage_kafkaimageprocessor_pvc_storageclass` and `mas_manage_kafkaimageprocessor_pvc_size` format
- [x] Template variables use `mas_manage_civil_kafka_image_processor_pvc` format

#### 6.4 Ensure storage class logic matches other PVC configurations ✅
- [x] Uses same `mas_app_settings_default_pvc_storage_class` (RWX)
- [x] Includes in storage class assertion checks
- [x] Auto-detection only when not user-provided

## Testing Checklist

After implementation:
1. Test with civil component enabled and PVC variables set
2. Test with civil component enabled but PVC variables not set (should use defaults)
3. Test with civil component disabled (should not configure PVC)
4. Test storage class auto-detection when not specified
5. Verify ManageWorkspace CR contains correct `spec.components.civil.persistentVolumeClaims.kafkaImageProcessor` structure

## Integration with Operator

This ansible-devops work integrates with the operator changes in:
`C:\Users\097891866\Documents\GitHub\maximoappsuite\ibm-mas-manage\.bob\plans\2026-05-10-kafka-image-processor-pvc-management.md`

The operator expects:
```yaml
spec:
  components:
    civil:
      persistentVolumeClaims:
        kafkaImageProcessor:
          size: "10Gi"
          storageClassName: "ibmc-file-gold"
```

This ansible role will generate that structure when the environment variables are set.
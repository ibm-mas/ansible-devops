# Variable Documentation Enhancement Plan

## Executive Summary

This document outlines a focused plan to enhance variable documentation across all role README files in the `ibm.mas_devops` Ansible collection. The goal is to improve clarity, completeness, and usability of variable descriptions without adding code examples.

## Current State Assessment

### Identified Issues

After reviewing role README files, the following variable documentation issues were identified:

1. **Vague or Brief Descriptions**
   - "Defines the instance ID" - doesn't explain what an instance ID is or its purpose
   - "MongoDB provider" - lacks context about available options and when to use each
   - "Set this to true" - missing explanation of what happens when enabled

2. **Missing Context**
   - No explanation of when optional variables should be set vs. left as default
   - Unclear about the impact of changing a variable
   - Missing guidance on choosing between multiple valid values

3. **Unclear Relationships**
   - Dependencies between variables not documented
   - Mutually exclusive variables not identified
   - Required combinations not explained

4. **Incomplete Metadata**
   - Valid value ranges not specified
   - Format requirements unclear (e.g., URL format, version format)
   - Version-specific behavior not documented
   - Deprecation status not clearly marked

5. **Missing "Why" Information**
   - Purpose of the variable not explained
   - Use cases not provided
   - Business/technical rationale absent

## Enhancement Framework

### Standard Variable Documentation Template

Each variable should follow this enhanced structure:

```markdown
#### variable_name
[One-sentence summary of what the variable controls]

**Purpose**: [Detailed explanation of why this variable exists and what it accomplishes]

**When to use**: [Guidance on when to set this variable vs. using defaults]
- [Scenario 1]
- [Scenario 2]

**Valid values**: [Specific values, ranges, or format requirements]

**Impact**: [What happens when this variable is set/changed]

**Related variables**: [List of variables that interact with this one]

- **Required/Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default: `value` or None

**Note**: [Any warnings, version-specific behavior, or deprecation notices]
```

### Enhancement Guidelines

#### 1. Purpose Statement
Every variable must have a clear purpose statement that explains:
- What the variable controls
- Why it exists
- What problem it solves
- What it enables or configures

**Good**: "Controls the MongoDB version to be deployed. This allows you to align with MAS compatibility requirements or maintain consistency across environments."

**Bad**: "Defines the MongoDB version."

#### 2. When to Use Guidance
For optional variables, provide clear guidance on:
- Common scenarios where the variable should be set
- When to use default values
- When to override defaults
- Decision criteria for choosing values

**Good**:
```
**When to use**:
- Set to `false` in development environments to speed up deployments
- Set to `true` in production to ensure compliance with security policies
- Leave as default for standard installations
```

**Bad**: "Optional variable for configuration."

#### 3. Valid Values Documentation
Clearly specify:
- Exact valid values for enumerated options
- Format requirements (URLs, version strings, etc.)
- Value ranges for numeric variables
- Pattern requirements for strings

**Good**: "Valid values: `community`, `ibm`, `aws` (case-sensitive)"

**Bad**: "Provider type."

#### 4. Impact Description
Explain what happens when the variable is:
- Set to a specific value
- Changed from default
- Left unset

**Good**: "When set to `true`, the role will create a ClusterIssuer for Let's Encrypt certificate automation. This enables automatic certificate renewal but requires DNS provider credentials."

**Bad**: "Enables certificate management."

#### 5. Related Variables
Document:
- Variables that must be set together
- Variables that are mutually exclusive
- Variables that affect this variable's behavior
- Variables affected by this variable

**Good**: "Related variables: Must be set together with `mas_instance_id`. Affects `mas_config_dir` output location."

**Bad**: None provided.

#### 6. Notes and Warnings
Include:
- Version-specific behavior
- Deprecation notices
- Important warnings
- Known limitations
- Breaking changes

**Good**: "**Note**: Deprecated in SLS 3.8.0. Use `sls_icr_cpopen` instead. This variable is only required for SLS versions 3.7.0 and earlier."

**Bad**: "Deprecated."

## Implementation Approach

### Phase 1: High-Priority Roles (Week 1)
Focus on most frequently used roles:

1. **suite_install** (~30 variables)
2. **mongodb** (~40 variables)
3. **suite_app_install** (~25 variables)
4. **sls** (~35 variables)
5. **suite_config** (~20 variables)

**Estimated effort**: 2-3 hours per role

### Phase 2: Infrastructure Roles (Week 2)
Core infrastructure and dependency roles:

1. **cert_manager** (~5 variables)
2. **suite_dns** (~30 variables)
3. **db2** (~35 variables)
4. **kafka** (~20 variables)
5. **ibm_catalogs** (~10 variables)

**Estimated effort**: 1-3 hours per role

### Phase 3: Application Roles (Week 3)
Application-specific configuration roles:

1. **suite_app_config** (~20 variables)
2. **suite_manage_pvc_config** (~15 variables)
3. **cp4d** (~40 variables)
4. **aiservice** (~25 variables)
5. **suite_app_upgrade** (~15 variables)

**Estimated effort**: 1-2 hours per role

### Phase 4: Remaining Roles (Week 4)
All other roles in alphabetical order:

- Backup/restore roles
- OCP provisioning roles
- Mirror/airgap roles
- Monitoring roles
- Utility roles

**Estimated effort**: 0.5-2 hours per role

## Quality Standards

### Variable Documentation Checklist

For each variable, verify:

- [ ] **Clear one-sentence summary** provided
- [ ] **Purpose statement** explains the "why"
- [ ] **When to use guidance** provided for optional variables
- [ ] **Valid values** clearly specified with format/range
- [ ] **Impact description** explains what happens when set
- [ ] **Related variables** documented if applicable
- [ ] **Required/Optional** status is correct
- [ ] **Environment variable** name is accurate
- [ ] **Default value** matches actual code
- [ ] **Notes/warnings** included for special cases
- [ ] **Version-specific behavior** documented if applicable
- [ ] **Deprecation status** clearly marked if deprecated
- [ ] **No technical jargon** without explanation
- [ ] **Consistent terminology** with other variables
- [ ] **Proper grammar and spelling** throughout

### Review Process

1. **Self-review**: Author checks against quality checklist
2. **Peer review**: Another team member reviews for clarity
3. **Technical review**: Subject matter expert verifies accuracy
4. **User testing**: Sample users validate understandability

## Example Transformations

### Example 1: Basic Variable Enhancement

**Before:**
```markdown
#### mas_channel
Defines which channel of MAS to subscribe to.

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default: None
```

**After:**
```markdown
#### mas_channel
Specifies the MAS operator subscription channel, which determines the version stream you'll receive updates from.

**Purpose**: Controls which version of MAS will be installed and which updates will be automatically applied. The channel corresponds to major.minor version releases and determines the feature set and compatibility level.

**When to use**:
- Set to the latest stable channel for new production deployments
- Use specific older channels when compatibility with existing applications requires it
- Consult the MAS compatibility matrix before selecting a channel
- Change channels only during planned upgrade windows

**Valid values**: `8.9.x`, `8.10.x`, `8.11.x`, `9.0.x` (check the IBM Operator Catalog for currently available channels)

**Impact**: Changing the channel will trigger an upgrade to the latest version in that channel. This may require application reconfiguration and testing.

**Related variables**: Works with `mas_catalog_source` to determine available channels.

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default: None

**Note**: Once installed, changing channels requires careful planning. Review the upgrade documentation before changing this value.
```

### Example 2: Optional Variable with Defaults

**Before:**
```markdown
#### mongodb_storage_capacity_data
The size of the PVC that will be created for data storage in the cluster.

- **Optional**
- Environment Variable: `MONGODB_STORAGE_CAPACITY_DATA`
- Default Value: `20Gi`
```

**After:**
```markdown
#### mongodb_storage_capacity_data
Specifies the size of the persistent volume claim (PVC) allocated for MongoDB data storage on each replica set member.

**Purpose**: Determines the amount of disk space available for storing MongoDB databases, collections, and indexes. Proper sizing prevents storage exhaustion and ensures adequate space for data growth.

**When to use**:
- Increase from default for production environments with large data volumes
- Increase for environments with high data growth rates
- Use default (20Gi) for development, testing, or small deployments
- Consider your backup strategy when sizing (larger volumes take longer to backup)

**Valid values**: Any valid Kubernetes storage size (e.g., `20Gi`, `100Gi`, `500Gi`, `1Ti`)

**Impact**:
- Larger values consume more cluster storage resources
- Cannot be decreased after deployment (PVC expansion only)
- Total storage = this value × number of replicas
- Affects backup and restore duration

**Related variables**:
- `mongodb_replicas`: Total storage = capacity × replicas
- `mongodb_storage_class`: Must support volume expansion if you plan to increase size later
- `mongodb_storage_capacity_logs`: Consider balancing data and log storage

- **Optional**
- Environment Variable: `MONGODB_STORAGE_CAPACITY_DATA`
- Default Value: `20Gi`

**Note**: PVCs can be expanded but not shrunk. Plan for growth when setting initial size. Monitor storage usage to avoid running out of space.
```

### Example 3: Provider-Specific Variable

**Before:**
```markdown
#### mongodb_provider
MongoDB provider, choose whether to use the MongoDb Community Edition Operator (`community`), IBM Cloud Database for MongoDb (`ibm`), or AWS DocumentDb (`aws`).

- **Optional**
- Environment Variable: `MONGODB_PROVIDER`
- Default Value: `community`
```

**After:**
```markdown
#### mongodb_provider
Selects which MongoDB deployment option to use for MAS database requirements.

**Purpose**: Determines the MongoDB infrastructure provider, which affects deployment architecture, management approach, operational requirements, and cost model. Each provider offers different trade-offs between control, convenience, and cost.

**When to use**:
- Use `community` for self-managed deployments with full control and no cloud dependencies
- Use `ibm` for managed service on IBM Cloud with automated backups and scaling
- Use `aws` for managed DocumentDB service on AWS with AWS ecosystem integration
- Consider operational expertise, cloud platform, and management preferences

**Valid values**:
- `community` - MongoDB Community Edition Operator (self-managed on OpenShift)
- `ibm` - IBM Cloud Databases for MongoDB (managed service)
- `aws` - AWS DocumentDB (managed service, MongoDB-compatible)

**Impact**:
- `community`: Requires cluster storage, manual backup management, and operational overhead
- `ibm`: Requires IBM Cloud account, API key, and incurs IBM Cloud service charges
- `aws`: Requires AWS account, VPC configuration, and incurs AWS service charges

**Related variables**:
- When `ibm`: Requires `ibmcloud_apikey`, `ibm_mongo_region`, `ibm_mongo_resourcegroup`
- When `aws`: Requires `aws_access_key_id`, `aws_secret_access_key`, `vpc_id`, `docdb_*` variables
- When `community`: Requires `mongodb_storage_class` and related storage variables

- **Optional**
- Environment Variable: `MONGODB_PROVIDER`
- Default Value: `community`

**Note**: Provider cannot be changed after initial deployment. Migration between providers requires backup and restore procedures.
```

### Example 4: Deprecated Variable

**Before:**
```markdown
#### ibm_entitlement_key
Provide your IBM entitlement key.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None
```

**After:**
```markdown
#### ibm_entitlement_key
IBM entitlement key for accessing IBM Container Registry images.

**Purpose**: Authenticates access to IBM's entitled container registry to pull SLS operator and component images. This key is tied to your IBM Cloud account and product entitlements.

**When to use**:
- Required for SLS versions 3.7.0 and earlier
- Not required for SLS 3.8.0 and later (images moved to public registry)
- Obtain from IBM Container Library at https://myibm.ibm.com/products-services/containerlibrary

**Valid values**:
- IBM entitlement key string (typically starts with "eyJ...")
- Must be a valid, non-expired key with SLS entitlements

**Impact**:
- Invalid or expired keys will cause image pull failures
- Key is stored in a Kubernetes secret in the SLS namespace
- Used to create image pull secrets for SLS pods

**Related variables**:
- `sls_entitlement_username`: Username paired with this key (default: `cp`)
- `sls_catalog_source`: Must point to catalog requiring this authentication

- **Required** for SLS 3.7.0 and earlier
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Note**: **DEPRECATED in SLS 3.8.0** - SLS images moved to public registry (`icr.io/cpopen`). This variable is only required for SLS versions up to 3.7.0. For SLS 3.8.0+, no entitlement key is needed.
```

## Success Metrics

### Quantitative Metrics
1. **Completion Rate**: % of variables with all checklist items completed
2. **Consistency Score**: % of variables following the standard template
3. **Completeness Score**: Average number of template sections completed per variable

**Targets**:
- 100% completion rate for Phase 1 roles
- 95%+ consistency score across all enhanced variables
- 90%+ completeness score (all sections present where applicable)

### Qualitative Metrics
1. **User Feedback**: Survey responses on documentation clarity
2. **Support Ticket Reduction**: Decrease in variable-related questions
3. **Time to Understanding**: User testing of comprehension speed

**Targets**:
- Positive feedback from 80%+ of surveyed users
- 30% reduction in variable-related support questions
- 40% faster comprehension in user testing

## Maintenance Process

### For New Variables
1. Use the standard template when documenting new variables
2. Complete all applicable sections
3. Include in peer review checklist
4. Verify against quality standards before merge

### For Existing Variables
1. Enhance during role updates or bug fixes
2. Prioritize frequently used or confusing variables
3. Update when behavior changes
4. Refresh when deprecation occurs

### Ongoing Quality
1. Monthly review of user feedback on variable documentation
2. Quarterly audit of variable documentation completeness
3. Update template based on lessons learned
4. Maintain consistency across all roles

## Tools and Resources

### Documentation Tools
- **Template file**: `build/scripts/templates/VARIABLE_TEMPLATE.md`
- **Checklist**: Quality standards checklist (above)
- **Review guide**: Peer review guidelines

### Reference Materials
- Existing role code for accurate defaults
- MAS product documentation for context
- Compatibility matrix for version information
- Support ticket history for common issues

## Next Steps

1. **Review and approve** this focused enhancement plan
2. **Create template file** for variable documentation
3. **Select pilot role** (recommend: mongodb or suite_install)
4. **Enhance pilot role variables** following the framework
5. **Gather feedback** from team and users
6. **Refine approach** based on pilot results
7. **Roll out** to remaining roles per priority phases
8. **Track metrics** and adjust as needed

---

**Document Version**: 1.0
**Created**: 2026-01-13
**Owner**: DevOps Documentation Team
**Status**: Ready for Implementation
**Scope**: Variable Documentation Enhancement Only (No Code Examples)
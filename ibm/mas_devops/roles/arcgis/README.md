arcgis
===============================================================================

Installs **IBM Maximo Location Services for Esri**.

This dependency is an alternative solution if you are planning to leverage geospatial and map features with Maximo Spatial.
The biggest benefit of using it is that you could have both IBM Maximo Location Services for Esri and Maximo Spatial deployed and running into the same cluster, which improves significantly your overall networking performance.

**Note:** IBM Maximo Location Services for Esri will make use of MAS cluster issuers while managing internal and public certificates thus, you while using [suite_dns](suite_dns.md) to setup cluster issuer and public certificates for your MAS instances, these are automatically reused for your instance of `IBM Maximo Location Services for Esri`.

### Deployment details

Here are the full deployment details for a default installation, considering number of running pods, cpu/memory and storage utilization:

```bash
oc get deployments -n mas-$MAS_INSTANCE_ID-arcgis
NAME                                                    READY   UP-TO-DATE   AVAILABLE   AGE
arcgis-enterprise-apps                                  1/1     1            1           101m
arcgis-enterprise-manager                               1/1     1            1           114m
arcgis-enterprise-portal                                1/1     1            1           101m
arcgis-enterprise-web-style-app                         1/1     1            1           101m
arcgis-featureserver-webhook-processor                  1/1     1            1           74m
arcgis-gpserver-webhook-processor                       1/1     1            1           74m
arcgis-help                                             1/1     1            1           114m
arcgis-ingress-controller                               1/1     1            1           115m
arcgis-javascript-api                                   1/1     1            1           101m
arcgis-ki7vnxghb8526ejnxiqcf-mapserver                  1/1     1            1           82m
arcgis-kphc76hvhto7lzv74xxts-featureserver              1/1     1            1           73m
arcgis-kvrl4t01w78hbbyl1fsof-mapserver                  1/1     1            1           77m
arcgis-private-ingress-controller                       2/2     2            2           106m
arcgis-rest-administrator-api                           1/1     1            1           114m
arcgis-rest-services-api                                1/1     1            1           97m
arcgis-service-lifecycle-manager                        1/1     1            1           97m
arcgis-system-cachingcontrollers-gpserver               1/1     1            1           89m
arcgis-system-cachingcontrollers-gpsyncserver           1/1     1            1           89m
arcgis-system-cachingtools-gpserver                     1/1     1            1           89m
arcgis-system-cachingtools-gpsyncserver                 1/1     1            1           89m
arcgis-system-featureservicetools-gpserver              1/1     1            1           84m
arcgis-system-featureservicetools-gpsyncserver          1/1     1            1           84m
arcgis-system-publishingtools-gpserver                  1/1     1            1           89m
arcgis-system-publishingtools-gpsyncserver              3/3     3            3           89m
arcgis-system-reportingtools-gpserver                   1/1     1            1           89m
arcgis-system-spatialanalysistools-gpserver             1/1     1            1           82m
arcgis-system-spatialanalysistools-gpsyncserver         1/1     1            1           82m
arcgis-system-synctools-gpserver                        1/1     1            1           84m
arcgis-system-synctools-gpsyncserver                    1/1     1            1           84m
arcgis-utilities-geocodingtools-gpserver                1/1     1            1           80m
arcgis-utilities-geocodingtools-gpsyncserver            1/1     1            1           80m
arcgis-utilities-geometry-geometryserver                1/1     1            1           81m
arcgis-utilities-offlinepackaging-gpserver              1/1     1            1           79m
arcgis-utilities-offlinepackaging-gpsyncserver          1/1     1            1           79m
arcgis-utilities-printingtools-gpserver                 1/1     1            1           80m
arcgis-utilities-symbols-symbolserver-                  1/1     1            1           79m
ibm-mas-arcgis-entitymgr-ws                             1/1     1            1           118m
ibm-mas-arcgis-operator                                 1/1     1            1           121m
```

Total of `49` running pods.

```bash
oc adm top pods -n mas-$MAS_INSTANCE_ID-arcgis
NAME                                                              CPU(cores)   MEMORY(bytes)
arcgis-enterprise-apps                                              1m           105Mi
arcgis-enterprise-manager                                           0m           132Mi
arcgis-enterprise-portal                                            1m           144Mi
arcgis-enterprise-web-style-app                                     1m           80Mi
arcgis-featureserver-webhook-processor                              2m           426Mi
arcgis-gpserver-webhook-processor                                   5m           438Mi
arcgis-help                                                         1m           96Mi
arcgis-in-memory-store                                              5m           378Mi
arcgis-ingress-controller                                           2m           122Mi
arcgis-javascript-api                                               0m           12Mi
arcgis-ki7vnxghb8526ejnxiqcf-mapserver                              8m           1102Mi
arcgis-kphc76hvhto7lzv74xxts-featureserver                          4m           2250Mi
arcgis-kvrl4t01w78hbbyl1fsof-mapserver                              8m           934Mi
arcgis-object-store                                                 29m          3355Mi
arcgis-private-ingress-controller                                   4m           114Mi
arcgis-private-ingress-controller                                   2m           113Mi
arcgis-queue-store-cgatl-0                                          16m          186Mi
arcgis-relational-store-pfxpx-mcap-0                                14m          894Mi
arcgis-relational-store-pfxpx-yjnr-0                                4m           687Mi
arcgis-rest-administrator-api                                       26m          706Mi
arcgis-rest-metrics-api-nmbtw-0                                     4m           62Mi
arcgis-rest-portal-api-rpcnv-0                                      4m           678Mi
arcgis-rest-services-api                                            24m          876Mi
arcgis-service-lifecycle-manager                                    6m           744Mi
arcgis-spatiotemporal-index-store-dejcm-coordinator-0               4m           3612Mi
arcgis-system-cachingcontrollers-gpserver                           12m          919Mi
arcgis-system-cachingcontrollers-gpsyncserver                       2m           1179Mi
arcgis-system-cachingtools-gpserver                                 7m           906Mi
arcgis-system-cachingtools-gpsyncserver                             1m           1273Mi
arcgis-system-featureservicetools-gpserver                          7m           985Mi
arcgis-system-featureservicetools-gpsyncserver                      6m           977Mi
arcgis-system-publishingtools-gpserver                              13m          1043Mi
arcgis-system-publishingtools-gpsyncserver                          8m           939Mi
arcgis-system-publishingtools-gpsyncserver                          10m          1189Mi
arcgis-system-publishingtools-gpsyncserver                          16m          891Mi
arcgis-system-reportingtools-gpserver                               20m          636Mi
arcgis-system-spatialanalysistools-gpserver                         8m           982Mi
arcgis-system-spatialanalysistools-gpsyncserver                     14m          927Mi
arcgis-system-synctools-gpserver                                    11m          1093Mi
arcgis-system-synctools-gpsyncserver                                23m          960Mi
arcgis-utilities-geocodingtools-gpserver                            24m          959Mi
arcgis-utilities-geocodingtools-gpsyncserver                        10m          1189Mi
arcgis-utilities-geometry-geometryserver                            6m           1053Mi
arcgis-utilities-offlinepackaging-gpserver                          19m          983Mi
arcgis-utilities-offlinepackaging-gpsyncserver                      6m           914Mi
arcgis-utilities-printingtools-gpserver                             21m          1323Mi
arcgis-utilities-symbols-symbolserver                               9m           580Mi
ibm-mas-arcgis-entitymgr-ws                                         1222m        201Mi
ibm-mas-arcgis-operator                                             0m           48Mi
```

Average of `1650` milicores (1.65 vCPUs) and `40` gigabytes of memory RAM.

```bash
oc get pvc -n mas-$MAS_INSTANCE_ID-arcgis
NAME                                                                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      AGE
arcgis-in-memory-store-feiz3-0-data-volume                          Bound    pvc-432e190c-dbe4-44d5-828b-bf8126a326fe   20Gi       RWO            ibmc-block-gold   108m
arcgis-rest-portal-api-rpcnv-0-portal-sharing-volume                Bound    pvc-a1201747-6b7e-42b8-beed-c842c21cfa01   20Gi       RWO            ibmc-block-gold   62m
data-volume-arcgis-object-store-o0vq5-awsrx-0                       Bound    pvc-6c97716f-20d4-46b2-a110-706546dda95d   32Gi       RWO            ibmc-block-gold   108m
data-volume-arcgis-relational-store-pfxpx-mcap-0                    Bound    pvc-28635771-0e4a-475d-b6aa-2012c48dd470   20Gi       RWO            ibmc-block-gold   111m
data-volume-arcgis-relational-store-pfxpx-yjnr-0                    Bound    pvc-0e2dbc22-11af-4c5c-b5e7-b00d21a060fe   20Gi       RWO            ibmc-block-gold   100m
data-volume-arcgis-spatiotemporal-index-store-dejcm-coordinator-0   Bound    pvc-2e0ca0f0-c830-4353-abf0-196ce0e75b87   20Gi       RWO            ibmc-block-gold   108m
prometheus-volume-arcgis-rest-metrics-api-nmbtw-0                   Bound    pvc-fbc5c0ce-26eb-441f-8161-2191fd113a80   30Gi       RWO            ibmc-block-gold   108m
queue-data-volume-arcgis-queue-store-cgatl-0                        Bound    pvc-93451297-0e3d-4a56-bf4e-cff9bda43fb7   20Gi       RWO            ibmc-block-gold   108m
```

Average of 182 gigabyes of required capacity.

Role Variables - Installation
-------------------------------------------------------------------------------
### ibm_entitlement_key
IBM entitlement key for accessing container images.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Authenticates access to IBM container registry for pulling IBM Maximo Location Services for Esri images.

**When to use**: Required for all ArcGIS installations. Obtain from [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary).

**Valid values**: Valid IBM entitlement key string from your IBM account.

**Impact**: Without a valid key, the ArcGIS operator and component images cannot be pulled and installation will fail.

**Related variables**: None

**Notes**:
- Keep the entitlement key secure and do not commit it to version control
- The key is associated with your IBM ID and product entitlements
- Verify key validity before deployment to avoid installation failures

### mas_catalog_source
Catalog source for MAS operator installation.

- Optional
- Environment Variable: `MAS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

**Purpose**: Specifies which operator catalog to use for installing IBM Maximo Location Services for Esri.

**When to use**: The default is appropriate for both release and development installations. Override only if using a custom or mirrored catalog.

**Valid values**:
- `ibm-operator-catalog` (default) - Standard IBM operator catalog
- Custom catalog name for airgap or development environments

**Impact**: Determines the source of operator images and available versions.

**Related variables**: [`mas_arcgis_channel`](#mas_arcgis_channel)

**Notes**: For airgap installations, ensure the catalog has been properly mirrored with all required ArcGIS images.

### mas_arcgis_channel
Subscription channel for IBM Maximo Location Services for Esri operator.

- Optional
- Environment Variable: `MAS_ARCGIS_CHANNEL`
- Default: `9.1.x`

**Purpose**: Controls which version stream of IBM Maximo Location Services for Esri will be installed and receive updates.

**When to use**: Override the default when you need a specific version or want to control upgrade timing. The channel determines which updates are automatically applied.

**Valid values**: Version-specific channels (e.g., `9.1.x`, `9.0.x`)

**Impact**: Determines the ArcGIS version installed and which automatic updates are received. Changing channels may trigger upgrades.

**Related variables**: [`mas_catalog_source`](#mas_catalog_source)

**Notes**:
- The `9.1.x` channel receives updates within the 9.1 version stream
- Review release notes before changing channels
- Channel changes may require operator restarts

Role Variables - MAS Configuration
-------------------------------------------------------------------------------
### mas_instance_id
MAS instance identifier for ArcGIS deployment.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Associates the IBM Maximo Location Services for Esri deployment with a specific MAS instance.

**When to use**: Required when deploying ArcGIS for a specific MAS instance. The ArcGIS namespace will be created as `mas-<instance-id>-arcgis`.

**Valid values**: Valid MAS instance ID (lowercase alphanumeric, max 12 characters)

**Impact**: Determines the namespace where ArcGIS will be deployed and which MAS instance it will integrate with.

**Related variables**: None

**Notes**:
- The deployment namespace will be `mas-<mas_instance_id>-arcgis`
- ArcGIS will automatically use the MAS cluster issuers for certificate management
- Ensure the MAS instance exists before deploying ArcGIS

### custom_labels
Custom labels to apply to ArcGIS instance resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Enables tagging of ArcGIS resources with custom metadata for organization, tracking, or automation purposes.

**When to use**: When you need to apply organizational labels for cost tracking, environment identification, or resource management.

**Valid values**: Comma-separated list of key=value pairs (e.g., `env=prod,team=spatial,cost-center=12345`)

**Impact**: Labels are applied to instance-specific ArcGIS resources for identification and filtering.

**Related variables**: None

**Notes**:
- Labels must follow Kubernetes label syntax (alphanumeric, hyphens, underscores, dots)
- Useful for cost allocation, resource queries, and automation scripts
- Applied to all 49 ArcGIS deployment resources


Example Playbooks
-------------------------------------------------------------------------------
### Install IBM Maximo Location Services for Esri
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibm_entitlement_key: xxx
  roles:
    - ibm.mas_devops.ibm_catalogs
    - ibm.mas_devops.arcgis
```

License
-------------------------------------------------------------------------------

EPL-2.0

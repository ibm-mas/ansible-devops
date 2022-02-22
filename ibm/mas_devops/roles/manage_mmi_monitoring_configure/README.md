manage_mmi_monitoring_configure
================================

This role enables the pod monitoring service for manage app via mmi monitoring. 

Requirements
------------

MAS Manage app has to be installed. 

Role Variables
--------------

### MAS_INSTANCE_ID

required. The name of mas instance. 
 * Environment Variable: MAS_INSTANCE_ID
 * Default Value: none

### MAS_WORKSPACE_ID

required. The name of mas workspace. 
 * Environment Variable: MAS_WORKSPACE_ID
 * Default Value: none

### MANAGE_APP_TYPE_NAME

required. The name of mas manage bundle type. 
 * Environment Variable: MANAGE_APP_TYPE_NAME
 * Default Value: all

### PROMETHEUS_STORAGE_CLASS

required. The storageclass name of userload prometheus db. 
 * Environment Variable: PROMETHEUS_STORAGE_CLASS
 * Default Value: none

### PROMETHEUS_STORAGE_SIZE

required. The storageclass size of userload prometheus db. 
 * Environment Variable: PROMETHEUS_STORAGE_SIZE
 * Default Value: none


### PROMETHEUS_RETENTION_PERIOD

required. The retention period of userload prometheus db. 
 * Environment Variable: PROMETHEUS_RETENTION_PERIOD
 * Default Value: 90d

### PROMETHEUS_ALERTMGR_STORAGE_CLASS

required. The storageclass name of userload prometheus alert db. 
 * Environment Variable: PROMETHEUS_ALERTMGR_STORAGE_CLASS
 * Default Value: none

### PROMETHEUS_ALERTMGR_STORAGE_SIZE

required. The storageclass size of userload prometheus alert db. 
 * Environment Variable: PROMETHEUS_ALERTMGR_STORAGE_SIZE
 * Default Value: none

Dependencies
------------
N/A


License
-------

BSD

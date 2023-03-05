oc adm policy add-scc-to-user privileged -z sidb-sa -n oracle-database-operator-system

prebuiltdb-admin-secret

kind: SecurityContextConstraints
apiVersion: security.openshift.io/v1
metadata:
  name: sidb-scc
  namespace: oracle-database-operator
allowPrivilegedContainer: false
users:
 - system:serviceaccount:oracle-database-operator:sidb-sa
runAsUser:
  type: MustRunAsRange
  uidRangeMin: 0
  uidRangeMax: 60000
seLinuxContext:
  type: MustRunAs
fsGroup:
  type: MustRunAs
  ranges:
  - min: 0
    max: 60000
supplementalGroups:
  type: MustRunAs
  ranges:
  - min: 0
    max: 60000
volumes:
  - '*'
allowedCapabilities:
  - '*'

---
kind: SecurityContextConstraints
apiVersion: security.openshift.io/v1
metadata:
   name: sidb-scc
   namespace: oracle-database-operator-system
allowPrivilegedContainer: false
users:
    - 'system:serviceaccount:oracle-database-operator-system:sidb-sa'
runAsUser:
   type: MustRunAsRange
   uidRangeMin: 0
   uidRangeMax: 60000
seLinuxContext:
   type: RunAsAny
fsGroup:
   type: MustRunAs
   ranges:
   - min: 0
     max: 60000
supplementalGroups:
  type: MustRunAs
  ranges:
  - min: 0
    max: 60000
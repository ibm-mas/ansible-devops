# CP4D Playbooks

## Install CP4D
This playbook deploys Cloud Pak for Data 3.5.0 on the target cluster using OLM. URL and Credentials to access CP4D dashboard are displayed at the end of the playbook execution.

You can obtain the url for the CP4D dashboard at any time by running the following command: `oc get routes -n cpd-meta-ops`.  The credentials to sign-in are the defaults for CP4D, which are `admin/password`.

Yes, really!

### Required environment variables
- `CPD_ENTITLEMENT_KEY` An IBM entitlement key that includes access to Cloud Pak for Data 3.5.0

!!! note
    Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx

ansible-playbook playbooks/cp4d/install-cp4d.yml
```


## Install Db2
The db2wh instance installed by this playbook has SSL enabled. Certificates are available from the `internal-tls` secret in the `cpd-meta-ops` namespace.

The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.

!!! warning "TODO"
    Provide info how to access the db2 instance using a database client (e.g. dbeaver), also is there any kind of ui/dashboard in CP4D where we can see this thing?

### Required environment variables
- `CPD_STORAGE_CLASS` Provide the storage class to use for Db2

### Example usage
```bash
export CPD_STORAGE_CLASS=xxx

ansible-playbook playbooks/cp4d/install-db2.yml
```

You can examine the deployed resources in the `cpd-meta-ops` namespace:

```bash
oc -n cpd-meta-ops get cpdservice,db2ucluster

NAME                                                       MESSAGE                 REASON   STATUS       LASTACTION   PHASE        CODE
cpdservice.metaoperator.cpd.ibm.com/cpdservice-db2wh       Completed                        Ready        CPDInstall   Ready        0
cpdservice.metaoperator.cpd.ibm.com/cpdservice-db2wh-dmc   CPD binary is running            Installing   CPDInstall   Installing   1

NAME                                            STATE      AGE
db2ucluster.db2u.databases.ibm.com/db2u-bludb   NotReady   8m44s
```

!!! tip
    The playbook will generate a yaml file containing the definition of a Secret and JdbcCfg resource that can be used to configure the deployed cluster as the MAS system JDBC datasource.

    This file can be directly applied using `oc apply -f /tmp/jdbccfg-cp4ddb2wh-system.yaml` or added to the `mas_config` list variable used by the `mas.devops.suite_install` role to deploy and configure MAS.



## Install Spark
This playbook is simply installing spark and making it available via cp4d ui console, nothing else.

!!! warning "TODO"
    This isn't really doing anything **for MAS** right now, how is Spark used in MAS, how does it integrate to MAS?  The role and playbook **must** be updated to do more than just install Spark, or it will be removed.  Each item we introduce to the playbook must directly tie into MAS, otherwise we are just wasting our time.

    - What inside MAS uses Spark?
    - How does it use Spark?

    To make this playbook get everything set up exactly how MAS needs it, and make it possible to configure MAS to use it we need to answer those two basic questions first.

### Required environment variables
- `CPD_STORAGE_CLASS` Provide the storage class to use for Spark

### Optional environment variables
None

### Example usage
```bash
export CPD_STORAGE_CLASS=xxx

ansible-playbook playbooks/cp4d/install-spark.yml
```

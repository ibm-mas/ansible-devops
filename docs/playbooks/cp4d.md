# CP4D Playbooks
These playbooks deploys Cloud Pak for Data from the IBM Operator Catalog using the `v1.0` channel.

!!! warning
    The credentials to sign-in are the defaults for CP4D, which are `admin/password`.

    Yes, really!


## Required environment variables
The following required environment variables are common across all of the playbooks:

- `CPD_ENTITLEMENT_KEY` An [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary) that includes access to Cloud Pak for Data 3.5.0
- `CPD_STORAGE_CLASS` Provide the storage class to use for Db2
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files


## Lite install
This playbook will only install CP4D, none of the Cloud Pak's supported services will be enabled allowing you to set these up seperately.

### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-lite.yml
```


## DB2 install
This playbook will install CP4D, with **Db2 Warehouse** and **Db2 Management Console** enabled.

Additional a Db2 Warehouse cluster will be created and a public TLS encrypted route is configured to allow external access to the cluster. The certificates are available from the `internal-tls` secret in the `cpd-meta-ops` namespace.

The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.

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

    This file can be directly applied using `oc apply -f /tmp/jdbccfg-cp4ddb2wh-system.yaml` or added to the `mas_config` list variable used by the `ibm.mas_devops.suite_install` role to deploy and configure MAS.


### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-db2.yml
```

### Debugging Db2 install
The following command may come in handy:

```bash
oc -n cpd-meta-ops get formations.db2u.databases.ibm.com db2wh-db01 -o go-template='{{range .status.components}}{{printf "%s,%s,%s\n" .kind .name .status.state}}{{end}}' | column -s, -t
```

## Watson Studio install
This playbook will install CP4D with **Watson Studio** and a number of additional components to expand the base capability of Watson Studio enabled.

- **Watson Machine Learning** As part of Watson Studio, Watson Machine Learning helps data scientists and developers accelerate AI and machine learning deployment.
- **Apache Spark** Apache Spark is a runtime environment configured inside of Watson Studio similar to a Python Runtime environment.  When Spark is enabled from CP4D, you can opt to create a notebook and choose Spark as runtime to expand data modeling capabilities.
- **Watson AI OpenScale**  Watson OpenScale enables tracking AI models in production, validation and test models to mitigate operational risks.

For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mhmpmh-and-p-u/8.2.0?topic=started-getting-data-scientists)

!!! info "Application Support"
    - [Predict](https://www.ibm.com/docs/en/mas84/8.4.0?topic=applications-maximo-predict) requires Watson Studio, Machine Learning and Spark; Openscale is an optional dependency
    - [Health & Predict Utilities](https://www.ibm.com/docs/en/mas84/8.4.0?topic=solutions-maximo-health-predict-utilities) requires Watson Studio base capability only

### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-watsonstudio.yml
```

## Fullstack Install
This playbook will install CP4D, with all services that are supported by one or more applications in Maximo Application Suite enabled:

- **Db2 Warehouse** & **Db2 Management Console**
- **Watson Studio** with **Watson Machine Learning**, **Apache Spark**, & **Watson AI OpenScale**

For more information refer to the documentation for the individual Db2 and Watson Studio playbooks above.

### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-fullstack.yml
```

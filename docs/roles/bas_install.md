# BAS Role
The following role provide support to install BAS (Behavior Analytics Services ) and generate configuration that can be directly applied to Maximo Application Suite to support full automation of the deployment and configuration of a complete MAS system.

### Role facts
- `bas_namespace`  Namespace where BAS will be deployed, default is ibm-bas
- `bas_persistent_storage` Storage class of type filesystem that can be used by BAS and its persistent storage
- `bas_meta_storage_class` Storage class for metadata storage for BAS
!!! important
    For isntallation in IBM Cloud use ibmc-file-bronze-gid for persistent storage and ibmc-block-bronze for metadata.
- `bas_username` Username to be used within the BAS instance
- `bas_password` Password for the BAS user
- `grafana_username` Username for the Graphana Dashboard installed with BAS 
- `grafana_password` Password for Graphana dashboard installed with BAS

!!! note
    Following facts will hold the contact person information for you BAS instance

- `contact.email` E-mail from the contact person for BAS
- `contact.firstName` First name from the contact person for BAS 
- `contact.lastName` Last name from the contact person for BAS 
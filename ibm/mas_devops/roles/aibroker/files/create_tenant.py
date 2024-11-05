#!/usr/bin/env python3
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.

import datetime
import ibm_db
import sys
import os

if len(sys.argv) < 3:
    print("Usage: python3 create_tenant.py tenant_name sls_url dro_url ")
    print("Sample usage")
    print("Usage: python3 create_tenant.py kmodels-user3 sls_url dro_url")
    exit()

tenant_name = sys.argv[1]
sls_url = sys.argv[2]
dro_url = sys.argv[3]



# Retrieving schema
schema = os.getenv("NAMESPACE")
schema_uppercase = schema.upper()
print(schema_uppercase)
assert schema != None, "namespace env variable not found."

# Retrieving DB Details from env vars
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
db_name = os.getenv("db2_db")
db_username = os.getenv("db_username")
db_password = os.getenv("db_password")

assert db_host != None, "db_host env variable not found."
assert db_port != None, "db_port env variable not found."
assert db_name != None, "db_name env variable not found."
assert db_username != None, "db_username env variable not found."
assert db_password != None, "db_password env variable not found."

array = {ibm_db.SQL_ATTR_AUTOCOMMIT: ibm_db.SQL_AUTOCOMMIT_OFF}
conn = ibm_db.pconnect(f"Security=SSL;SSLServerCertificate=/tmp/db2-certificate.pem;DATABASE={db_name};HOSTNAME={db_host};PORT={db_port};PROTOCOL=TCPIP;UID={db_username};PWD={db_password};", "", "", array)
#conn = ibm_db.pconnect(f"DATABASE={db_name};HOSTNAME={db_host};PORT={db_port};PROTOCOL=TCPIP;UID={db_username};PWD={db_password};", "", "", array)





# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Adding entry in AIBROKER_TENANT table.
# - 
# --------------------------------------------------------------------------------------------------------------------------------

#statement_entitlement_string = f"INSERT INTO {schema}.AIBROKER_TENANT(NAME, STATUS, SLS_URL, DRO_URL) VALUES(?,?,?,?);"
statement_entitlement_string = f"INSERT INTO \"{schema_uppercase}\".AIBROKER_TENANT(NAME, STATUS, SLS_URL, DRO_URL) VALUES(?,?,?,?);"


stmt = ibm_db.prepare(conn, statement_entitlement_string)
ibm_db.bind_param(stmt, 1, tenant_name)
ibm_db.bind_param(stmt, 2, 'active')
ibm_db.bind_param(stmt, 3, sls_url)
ibm_db.bind_param(stmt, 4, dro_url)

try:
    stmt = ibm_db.execute(stmt)
except Exception as e:
    print("Transaction couldn't be completed. The Tenant has not been created")
    ibm_db.rollback(conn)
else:
    ibm_db.commit(conn)
    print("Transaction complete. The Tenant has been created.")



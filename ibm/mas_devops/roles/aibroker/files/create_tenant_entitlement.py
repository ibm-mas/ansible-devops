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

if len(sys.argv) < 5:
    print("Usage: python3 create_tenant_entitlement.py tenant_name  entitlement_type  model_type entilement_start_date entilement_end_date ")
    print("Sample usage")
    print("Usage: python3 create_tenant_entitlement.py kmodels-user3  standard pcc 2024-09-12 2025-09-12")
    exit()

tenant_name = sys.argv[1]

entitlement_type = sys.argv[2]
model_type = sys.argv[3]
entilement_start_date=sys.argv[4]
entilement_end_date=sys.argv[5]


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


# Retrirving entitlement_type id using entitlement_type and model_type

# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Retrirving entitlement_type id using entitlement_type and model_type
# - 
# --------------------------------------------------------------------------------------------------------------------------------
#entitlement_type_string = f"SELECT ID FROM {schema}.AIBROKER_ENTITLEMENT_TYPE WHERE ENTITLEMENT_TYPE = ? AND MODEL_TYPE = ?;"
entitlement_type_string = f"SELECT ID FROM \"{schema_uppercase}\".AIBROKER_ENTITLEMENT_TYPE WHERE ENTITLEMENT_TYPE = ? AND MODEL_TYPE = ?;"
print(entitlement_type_string)
stmt = ibm_db.prepare(conn, entitlement_type_string)
ibm_db.bind_param(stmt, 1, entitlement_type)
ibm_db.bind_param(stmt, 2, model_type)

try:
    ibm_db.execute(stmt)
    assert ibm_db.fetch_row(stmt) != False, "entitlement_type and model_type combination does not exist in database."
    entitlement_id = int(ibm_db.result(stmt, "ID"))
    print(f"Fetched entitlement id : {entitlement_id}")
except Exception as e:
    print(ibm_db.stmt_errormsg(stmt))
    print(f"Couldn't retrieve entitlement type from database. Exception : {e}")




# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Retrirving tenant id using tenant_name
# - 
# --------------------------------------------------------------------------------------------------------------------------------


#tenant_string = f"SELECT ID FROM {schema}.AIBROKER_TENANT WHERE NAME = ?;"
tenant_string = f"SELECT ID FROM \"{schema_uppercase}\".AIBROKER_TENANT WHERE NAME = ?;"
stmt = ibm_db.prepare(conn, tenant_string)
ibm_db.bind_param(stmt, 1, tenant_name)


try:
    ibm_db.execute(stmt)
    assert ibm_db.fetch_row(stmt) != False, "tenant_name does not exist in database."+tenant_name
    tenant_id = int(ibm_db.result(stmt, "ID"))
    print(f"Fetched tenant id : {tenant_id}")
except Exception as e:
    print(ibm_db.stmt_errormsg(stmt))
    print(f"Couldn't retrieve tenant id from database. Exception : {e}")


# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - insert into AIBROKER_TENANT_ENTITLEMENT
# - 
# --------------------------------------------------------------------------------------------------------------------------------


#statement_tenant_entitlement = f"INSERT INTO {schema}.AIBROKER_TENANT_ENTITLEMENT(TENANT_ID, ENTITLEMENT_ID, START_DATE, EXPIRE_DATE) VALUES(?,?,?,?);"
statement_tenant_entitlement = f"INSERT INTO \"{schema_uppercase}\".AIBROKER_TENANT_ENTITLEMENT(TENANT_ID, ENTITLEMENT_ID, START_DATE, EXPIRE_DATE) VALUES(?,?,?,?);"

stmt = ibm_db.prepare(conn, statement_tenant_entitlement)
ibm_db.bind_param(stmt, 1, tenant_id)
ibm_db.bind_param(stmt, 2, entitlement_id)
ibm_db.bind_param(stmt, 3, entilement_start_date )
ibm_db.bind_param(stmt, 4, entilement_end_date)

try:
    stmt = ibm_db.execute(stmt)
except Exception as e:
    print("Transaction couldn't be completed. The relationship of tenant and entitlement has not been created")
    ibm_db.rollback(conn)
else:
    ibm_db.commit(conn)
    print("Transaction complete. The relationship of tenant and entitlement has been created.")

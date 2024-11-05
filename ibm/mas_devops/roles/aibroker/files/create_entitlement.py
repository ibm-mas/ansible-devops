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

if len(sys.argv) < 8:
    print("Usage: python3 create_entitlement.py entitlement_type model_type allowed_number_of_model_training_per_month allowed_number_of_deployed_model_instance allowed_number_of_concurrent_training allowed_number_of_input allowed_watsonx_call allowed_file_size")
    print("Sample usage")
    print("Usage: python3 create_entitlement.py standard pcc 10 1 1 10000 100 1MB")
    exit()

entitlement_type = sys.argv[1]
model_type = sys.argv[2]
allowed_number_of_model_training_per_month = sys.argv[3]
allowed_number_of_deployed_model_instance = sys.argv[4]
allowed_number_of_concurrent_training = sys.argv[5]
allowed_number_of_input = sys.argv[6]
allowed_watsonx_call = sys.argv[7]
allowed_file_size = sys.argv[8]

if entitlement_type is None:
    entitlement_type = 'standard'

if model_type is None:
    model_type = 'pcc'

if allowed_number_of_model_training_per_month is None:
    allowed_number_of_model_training_per_month = 10

if allowed_number_of_deployed_model_instance is None:
    allowed_number_of_deployed_model_instance = 1
 
if allowed_number_of_concurrent_training is None:
    allowed_number_of_concurrent_training = 1

if allowed_number_of_input is None:
    allowed_number_of_input = 10000

if allowed_watsonx_call is None:
    allowed_watsonx_call = 10000

if allowed_file_size is None:
    allowed_file_size = '1MB'


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



# ct stores current time
ct = datetime.datetime.now()

array = {ibm_db.SQL_ATTR_AUTOCOMMIT: ibm_db.SQL_AUTOCOMMIT_OFF}

# use certificate to connect to DB2
conn = ibm_db.pconnect(f"Security=SSL;SSLServerCertificate=/tmp/db2-certificate.pem;DATABASE={db_name};HOSTNAME={db_host};PORT={db_port};PROTOCOL=TCPIP;UID={db_username};PWD={db_password};", "", "", array)

#statement_entitlement_string = "INSERT INTO AIBROKER.AIBROKER_ENTITLEMENT_TYPE (ENTITLEMENT_TYPE, MODEL_TYPE, ALLOWED_NUMBER_OF_MODEL_TRAINING_PER_MONTH, ALLOWED_NUMBER_OF_DEPLOYED_MODEL_INSTANCE, ALLOWED_NUMBER_OF_CONCURRENT_TRAINING, ALLOWED_NUMBER_OF_INPUT,ALLOWED_NUMBER_OF_WATSONX_CALL, ALLOWED_FILE_SIZE, CREATION_TIMESTAMP, UPDATED_TIMESTAMP) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?,?);"

statement_entitlement_string = f"INSERT INTO \"{schema_uppercase}\".AIBROKER_ENTITLEMENT_TYPE (ENTITLEMENT_TYPE, MODEL_TYPE, ALLOWED_NUMBER_OF_MODEL_TRAINING_PER_MONTH, ALLOWED_N
UMBER_OF_DEPLOYED_MODEL_INSTANCE, ALLOWED_NUMBER_OF_CONCURRENT_TRAINING, ALLOWED_NUMBER_OF_INPUT,ALLOWED_NUMBER_OF_WATSONX_CALL, ALLOWED_FILE_SIZE, CREATION_TIMESTAMP, UPDATED_TI
MESTAMP) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?,?);"
stmt = ibm_db.prepare(conn, statement_entitlement_string)
ibm_db.bind_param(stmt, 1, entitlement_type)
ibm_db.bind_param(stmt, 2, model_type)
ibm_db.bind_param(stmt, 3, allowed_number_of_model_training_per_month)
ibm_db.bind_param(stmt, 4, allowed_number_of_deployed_model_instance)
ibm_db.bind_param(stmt, 5, allowed_number_of_concurrent_training)
ibm_db.bind_param(stmt, 6, allowed_number_of_input)
ibm_db.bind_param(stmt, 7, allowed_watsonx_call)
ibm_db.bind_param(stmt, 8, allowed_file_size)
ibm_db.bind_param(stmt, 9, ct)
ibm_db.bind_param(stmt, 10, ct)
try:
    stmt = ibm_db.execute(stmt)
except Exception as e:
    print("Transaction couldn't be completed.")
    ibm_db.rollback(conn)
else:
    ibm_db.commit(conn)
    print("Transaction complete. AIBROKER_ENTITLEMENT_TYPE table has been populated.")

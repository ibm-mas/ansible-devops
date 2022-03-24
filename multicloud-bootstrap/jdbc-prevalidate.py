import jaydebeapi
import os
con=jaydebeapi.connect('com.ibm.db2.jcc.DB2Driver', 
                        os.getenv('MAS_JDBC_URL').replace(':sslConnection=true;',''),
                        {'user':os.getenv('MAS_JDBC_USER'),
                        'password':os.getenv('MAS_JDBC_PASSWORD'),
                        'sslConnection':'true',
                        'sslCertLocation':os.getenv('MAS_JDBC_CERT_LOCAL_FILE')},
                        jars=os.getenv('MAS_DB2_JAR_LOCAL_PATH'),)

if con :
#    print("Connected to db successfully !")
    con.close()
    os._exit(0)
else:
    os._exit(1)

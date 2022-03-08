#!/bin/bash
SCRIPT_STATUS=0

# Check if region is supported
if [[ $CLOUD_TYPE == "aws" ]]; then
    SUPPORTED_REGIONS="us-east-1;us-east-2;us-west-2;ca-central-1;eu-north-1;eu-south-1;eu-west-1;eu-west-2;eu-west-3;eu-central-1;ap-northeast-1;ap-northeast-2;ap-northeast-3;ap-south-1;ap-southeast-1;ap-southeast-2;sa-east-1"
else
    SUPPORTED_REGIONS=$DEPLOY_REGION
fi
if [[ ${SUPPORTED_REGIONS,,} =~ $DEPLOY_REGION ]]; then
  log "Supported region = PASS"
else
   log "ERROR: Supported region = FAIL"
   SCRIPT_STATUS=11
fi

# Check if ER key is valid
skopeo inspect --creds "cp:$SLS_ENTITLEMENT_KEY" docker://$MAS_IMAGE_TEST_DOWNLOAD > /dev/null
if [ $? -eq 0 ]; then
   log "ER key verification = PASS"
else
   log "ERROR: ER key verification = FAIL"
   SCRIPT_STATUS=12
fi

# Check if provided hosted zone is public
if [[ $CLOUD_TYPE == "aws" ]]; then
    aws route53 list-hosted-zones --output text --query 'HostedZones[*].[Config.PrivateZone,Name,Id]' --output text | grep $BASE_DOMAIN | grep False
else
    true
fi
if [ $? -eq 0 ]; then
   log "MAS public domain verification = PASS"
else
   log "ERROR: MAS public domain verification = FAIL"
   SCRIPT_STATUS=13
fi

# JDBC CFT inputs validation and  connection test
if [[ (-z $MAS_JDBC_USER) && (-z $MAS_JDBC_PASSWORD) && (-z $MAS_JDBC_URL) && (-z $MAS_JDBC_CERT_URL) ]]
then
    log "=== No Database details provided ==="
else
    if [ -z "$MAS_JDBC_USER" ] 
    then 
        log "ERROR: Database username is not specified"
        SCRIPT_STATUS=14
    elif [ -z "$MAS_JDBC_PASSWORD" ] 
    then 
        log "ERROR: Database password is not specified"
        SCRIPT_STATUS=14
    elif [ -z "$MAS_JDBC_URL" ] 
    then
        log "ERROR: Database connection url is not specified"
        SCRIPT_STATUS=14
    elif [ -z "$MAS_JDBC_CERT_URL" ] 
    then
        log "ERROR: Database certificate url is not specified"
        SCRIPT_STATUS=14
    else         
        log "Downloading DB certificate"
        cd $GIT_REPO_HOME
        if [[ ${MAS_JDBC_CERT_URL,,} =~ ^https? ]]; then
        wget "$MAS_JDBC_CERT_URL" -O db.crt
        log " MAS_JDBC_CERT_LOCAL_FILE=$MAS_JDBC_CERT_LOCAL_FILE"
        elif [[ ${MAS_JDBC_CERT_URL,,} =~ ^s3 ]]; then
        aws s3 cp "$MAS_JDBC_CERT_URL" db.crt
        log " MAS_JDBC_CERT_LOCAL_FILE=$MAS_JDBC_CERT_LOCAL_FILE"
        fi
        export MAS_DB2_JAR_LOCAL_PATH=$GIT_REPO_HOME/lib/db2jcc4.jar
        if  [[ $OFFERING_TYPE == "MAS Core + Manage (no Cloud Pak for Data)" ]]; then  
        if [[ ${MAS_JDBC_URL,, } =~ ^jdbc:db2? ]]; then
            log  "Connecting to the Database"
            if python jdbc-prevalidate.py;  then 
                log "JDBC URL Validation = PASS"
            else
                log "ERROR: JDBC URL Validation = FAIL"
                SCRIPT_STATUS=4
            fi
        else
            log "Skipping JDBC URL validation, supported only for DB2"     
            fi
        fi
       
    fi
fi

# Check if all the existing SLS inputs are provided
if [[ (-z $SLS_ENDPOINT_URL) && (-z $SLS_REGISTRATION_KEY) && (-z $SLS_PUB_CERT_URL) ]]
then
    log "=== New SLS Will be deployed ==="
else
    if [ -z "$SLS_ENDPOINT_URL" ] 
    then 
        log "ERROR: SLS Endpoint URL is not specified"
        SCRIPT_STATUS=15
    elif [ -z "$SLS_REGISTRATION_KEY" ] 
    then 
        log "ERROR: SLS Registration Key is not specified"
        SCRIPT_STATUS=15
    elif [ -z "$SLS_PUB_CERT_URL" ] 
    then
        log "ERROR: SLS Public Cerificate URL is not specified"
        SCRIPT_STATUS=15
    else         
        log "=== Using existing SLS deployment inputs ==="
    fi
fi

# Check if all the existing BAS inputs are provided 
if [[ (-z $BAS_API_KEY) && (-z $BAS_ENDPOINT_URL) && (-z $BAS_PUB_CERT_URL) ]]
then
    log "=== New BAS Will be deployed ==="
else
    if [ -z "$BAS_API_KEY" ] 
    then 
        log "ERROR: BAS API Key is not specified"
        SCRIPT_STATUS=16
    elif [ -z "$BAS_ENDPOINT_URL" ] 
    then 
        log "ERROR: BAS Endpoint URL is not specified"
        SCRIPT_STATUS=16
    elif [ -z "$BAS_PUB_CERT_URL" ] 
    then
        log "ERROR: BAS Public Cerificate URL is not specified"
        SCRIPT_STATUS=16
    else         
        log "=== Using existing BAS deployment inputs ==="
    fi
fi

# Check if all the existing OpenShift inputs are provided 
if [[ (-z $EXS_OCP_URL) && (-z $EXS_OCP_USER) && (-z $EXS_OCP_PWD) ]]
then
    log "=== New OCP Cluster and associated user and password will be deployed ==="
    if [[ -z $OCP_PULL_SECRET ]]; then
        log "ERROR: OpenShift pull secret is required for OCP cluster deployment"
        SCRIPT_STATUS=17
    fi
else
    if [ -z "$EXS_OCP_URL" ] 
    then 
        log "ERROR: Existing OCP Cluster URL is not specified"
        SCRIPT_STATUS=19
    elif [ -z "$EXS_OCP_USER" ] 
    then 
        log "ERROR: Existing OCP Cluster user is not specified"
        SCRIPT_STATUS=19
    elif [ -z "$EXS_OCP_PWD" ] 
    then
        log "ERROR: Existing OCP Cluster password is not specified"
        SCRIPT_STATUS=19
    else         
        log "=== Using existing OCP deployment inputs ==="
    fi
fi

# Check if MAS license is provided
if [[ -z $MAS_LICENSE_URL ]]; then
    log "ERROR: MAS license is reqiuired for MAS deployment"
    SCRIPT_STATUS=18
fi

exit $SCRIPT_STATUS

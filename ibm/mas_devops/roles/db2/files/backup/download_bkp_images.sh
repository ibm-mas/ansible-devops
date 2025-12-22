#!/bin/bash
set -o pipefail

# **********************************************************
# Download DB2 backup from IBMCOS
#
# Operation: DOWNLOAD_BACKUP
#
# Parameters:
#   $1  stgEndpoint - IBMCOS storage endpoint 
#   $2  access_key_id - IBMCOS access_key_id
#   $3  secret_access_key - IBMCOS secret_access_key
#   $$  ibm_cos_bucket - IBMCOS bucket
#   $5  ibm_cos_path - IBMCOS ibm_cos_path
#   $6  flex_db_name - Original migrated database name
#
#**********************************************************
#DOWNLOAD_BACKUP
function downloadDBBackup()
{
    stgEndpoint=$1
    access_key_id=$2
    secret_access_key=$3
    ibm_cos_bucket=$4
    ibm_cos_path=$5
    flex_db_name=$6
    download_path=$7
    file_name_to_be_downloaded=$8
    db2_version=$9
    cos_bucket_alias=${10}
    DOWNLOAD_BACK_LOG=~/bin/.DownloadBackupImagesLOG.out
    rm -f ${DOWNLOAD_BACK_LOG}

    echo "[INFO] DOWNLOAD_BACKUP" >> ${DOWNLOAD_BACK_LOG}   

    echo "[DEBUG] DOWNLOAD_BACKUP stgEndpoint: $stgEndpoint" >> ${DOWNLOAD_BACK_LOG}
    
    #echo "[DEBUG] DOWNLOAD_BACKUP access_key_id; $access_key_id"
    #echo "[DEBUG] DOWNLOAD_BACKUP secret_access_key: $secret_access_key"
    echo "[DEBUG] DOWNLOAD_BACKUP access_key_id; XXXXXXXXXX" >> ${DOWNLOAD_BACK_LOG}
    echo "[DEBUG] DOWNLOAD_BACKUP secret_access_key: XXXXXXXXXX" >> ${DOWNLOAD_BACK_LOG}

    echo "[DEBUG] DOWNLOAD_BACKUP ibm_cos_bucket: $ibm_cos_bucket" >> ${DOWNLOAD_BACK_LOG}
    echo "[DEBUG] DOWNLOAD_BACKUP ibm_cos_path: $ibm_cos_path" >> ${DOWNLOAD_BACK_LOG}
    echo "[DEBUG] DOWNLOAD_BACKUP ibm_cos_bucket: $ibm_cos_bucket" >> ${DOWNLOAD_BACK_LOG}
    echo "[DEBUG] DOWNLOAD_BACKUP ibm_cos_path: $ibm_cos_path" >> ${DOWNLOAD_BACK_LOG}
    echo "[DEBUG] DOWNLOAD_BACKUP flex_db_name: $flex_db_name" >> ${DOWNLOAD_BACK_LOG}
    echo "[DEBUG] DOWNLOAD_BACKUP download_path: $download_path" >> ${DOWNLOAD_BACK_LOG}
    echo "[DEBUG] DOWNLOAD_BACKUP file_name_to_be_downloaded: $file_name_to_be_downloaded" >> ${DOWNLOAD_BACK_LOG}
    if [ $db2_version == 'v11.5.7.0' ]; then
        db2RemStgManager S3 get server=${stgEndpoint} auth1=${access_key_id} auth2=${secret_access_key} container=${ibm_cos_bucket} source=${ibm_cos_path} target=$download_path/$file_name_to_be_downloaded 2>&1 | tee -a ${DOWNLOAD_BACK_LOG}
    else
        db2RemStgManager ALIAS GET source=DB2REMOTE://${cos_bucket_alias}/${ibm_cos_bucket}/${ibm_cos_path} target=$download_path/$file_name_to_be_downloaded 2>&1 | tee -a ${DOWNLOAD_BACK_LOG}
    fi
    rc=$?
    if [ $rc -ne 0 ]; then
        if [ $db2_version == 'v11.5.7.0' ]; then
            echo "FAILED_DOWNLOAD_BACKUP db2RemStgManager s3 get ${ibm_cos_path} target=$download_path/$file_name_to_be_downloaded rc=$rc" >> ${DOWNLOAD_BACK_LOG}
        else
            echo "FAILED_DOWNLOAD_BACKUP db2RemStgManager ALIAS GET source=DB2REMOTE://${cos_bucket_alias}/${ibm_cos_bucket}/${ibm_cos_path} target=$download_path/$file_name_to_be_downloaded rc=$rc" >> ${DOWNLOAD_BACK_LOG}
        fi
        echo "status=fail" >> ${DOWNLOAD_BACK_LOG}
        exit 1
    fi

    checkDownload=$(ls -1 $download_path/$file_name_to_be_downloaded)
    echo "[DEBUG] checkDownload= $checkDownload" >> ${DOWNLOAD_BACK_LOG}

    if [[  $checkDownload =~ "$download_path/$file_name_to_be_downloaded" ]]; then
        echo "[DEBUG] Backup image $file_name_to_be_downloaded donwloaded successfully" >> ${DOWNLOAD_BACK_LOG}
    else
        if [ $db2_version == 'v11.5.7.0' ]; then
            echo "FAILED_DOWNLOAD_BACKUP db2RemStgManager s3 get ${ibm_cos_path} target=$download_path/$file_name_to_be_downloaded rc=$rc" >> ${DOWNLOAD_BACK_LOG}
        else
            echo "FAILED_DOWNLOAD_BACKUP db2RemStgManager ALIAS GET source=DB2REMOTE://${cos_bucket_alias}/${ibm_cos_bucket}/${ibm_cos_path} target=$download_path/$file_name_to_be_downloaded rc=$rc" >> ${DOWNLOAD_BACK_LOG}
        fi
        echo "status=fail" >> ${DOWNLOAD_BACK_LOG}
        exit 1
    fi

    echo "status=success" | tee -a ${DOWNLOAD_BACK_LOG}
    sleep 5
    exit 0

}    

load_source_props=${11}
if [ "${load_source_props}" = true ]; then
    echo "Load from source props was true"
    source /mnt/backup/bin/.PROPS
    downloadDBBackup $SERVER $PARM1 $PARM2 $CONTAINER $5 $6 $7 $8 $9 ${10}
else
    echo "Load from source props was False"
    downloadDBBackup $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10}
fi
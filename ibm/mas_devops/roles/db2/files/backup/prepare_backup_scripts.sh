#!/bin/bash

# Finding the Instance owner
INSTOWNER=`/usr/local/bin/db2greg -dump | grep -ae "I," | grep -v "/das," | awk -F ',' '{print $4}' `

# Finding Instnace owner Group
GRPID=`cat /etc/passwd | grep ${INSTOWNER} | cut -d: -f4`
INSTGROUP=`cat /etc/group | grep ${GRPID} | cut -d: -f1`

# Find the home directory
INSTHOME=` cat /etc/passwd | grep ${INSTOWNER} | cut -d: -f6`

# Resolving INSTOWNER's executables path (sqllib):
DBPATH=`/usr/local/bin/db2greg -dump | grep -ae "I," | grep -v "/das," | grep "${INSTOWNER}" | awk -F ',' '{print $5}' `

# Source the db2profile for the root user to be able to issue several db2 commands locally:
SOURCEPATH="$DBPATH/db2profile"
. $SOURCEPATH

cd /tmp/db2-scripts/

echo -e "\nCopying the files to bin directory under Instance Home . . . "
cp -rp db2_backup.sh ${INSTHOME}/bin/

if [ -f setup_cos_storage_access.sh ]; then
    echo -e "\nCopying setup_cos_storage_access.sh to bin directory under Instance Home . . . "
    cp -rp setup_cos_storage_access.sh ${INSTHOME}/bin/
fi

chown -R ${INSTOWNER}:${INSTGROUP} ${INSTHOME}/bin

echo -e "\nINSTHOME=${INSTHOME}\n"
echo -e "PrepareSuccess: Backup scripts have been copied to Instance Home bin directory."

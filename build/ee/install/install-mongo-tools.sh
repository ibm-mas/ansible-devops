#!/bin/bash

# Install Mongo Shell
set -e

curl "https://downloads.mongodb.com/compass/mongodb-mongosh-shared-openssl3-2.2.9.x86_64.rpm" -o mongodb-mongosh-shared-openssl3-2.2.9.x86_64.rpm
rpm -i mongodb-mongosh-shared-openssl3-2.2.9.x86_64.rpm

mongosh --version
rm mongodb-mongosh-shared-openssl3-2.2.9.x86_64.rpm

# Install Mongo Tools
curl "https://fastdl.mongodb.org/tools/db/mongodb-database-tools-rhel90-x86_64-100.9.5.tgz" -o mongodb-database-tools-rhel90-x86_64-100.9.5.tgz
tar xvfz mongodb-database-tools-rhel90-x86_64-100.9.5.tgz

mv mongodb-database-tools-rhel90-x86_64-100.9.5/bin/* /usr/local/bin/
rm -rf mongodb-database-tools-rhel90-x86_64-100.9.5
rm mongodb-database-tools-rhel90-x86_64-100.9.5.tgz

mongodump --version

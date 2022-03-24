#####################################################################################################################
#
# Command to generate CSV file:
# -----------------------------
# export OFFLINEDIR=$HOME/offline
# export CASE_REPO_PATH=https://github.com/IBM/cloud-pak/raw/master/repo/case
# cloudctl case save \
#     --case ${CASE_REPO_PATH}/<case package name> \
#     --outputdir ${OFFLINEDIR}
#
# Comand to execute script:
# -------------------------
# ./create-ecr-repo.sh <AWS ACCESS KEY ID> <AWS SECRET ACCESS KEY> <AWS REGION> <AWS ACCOUNT ID> <CSV FILE PATH>
#
#####################################################################################################################

#!/bin/bash

ACCESS_KEY_ID=$1
SECRET_ACCESS_KEY=$2
AWS_REGION=$3
AWS_ACCOUNT_ID=$4
FILE_PATH=$5

# Install unzip and docker
sudo yum -y install unzip
sudo yum -y install docker

# Install AWS Cli
rm -rf "awscliv2.zip"
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" > /dev/null
unzip -o awscliv2.zip > /dev/null
sudo ./aws/install

# AWS Configure
aws configure set aws_access_key_id $ACCESS_KEY_ID; aws configure set aws_secret_access_key $SECRET_ACCESS_KEY; aws configure set default.region $AWS_REGION

# Authenticate to your default registry 
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

for repo_name in $(awk -F',' '{print $2}' $FILE_PATH | awk 'NR!=1 {print}' | awk '{print $NF}' FS=/) 
do 
echo $repo_name
aws ecr create-repository \
    --repository-name $repo_name \
    --image-scanning-configuration scanOnPush=true \
    --region $AWS_REGION
done


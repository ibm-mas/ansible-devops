#!/bin/bash

VPC_ID=$1
CLASSIC_LB_TIMEOUT=$2

#Install aws CLI
curl -O https://bootstrap.pypa.io/get-pip.py > /dev/null
python3 get-pip.py --user > /dev/null
export PATH="~/.local/bin:$PATH"
source ~/.bash_profile > /dev/null
pip install awscli --upgrade --user > /dev/null
pip install pssh > /dev/null

LOAD_BALANCER=`aws elb describe-load-balancers --output text | grep $VPC_ID | awk '{ print $5 }' | cut -d- -f1 | xargs`
for lbs in ${LOAD_BALANCER[@]}; do
aws elb modify-load-balancer-attributes --load-balancer-name $lbs --load-balancer-attributes "{\"ConnectionSettings\":{\"IdleTimeout\":$CLASSIC_LB_TIMEOUT}}"
done
#!/bin/bash

# Install AWS CLI
set -e

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install

rm -rf aws
rm  awscliv2.zip

aws --version

#!/bin/bash

# Install Rclone CLI
set -e

curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
unzip rclone-current-linux-amd64.zip

cp ./rclone-*-linux-amd64/rclone /usr/local/bin/

rclone version

rm -rf rclone-*

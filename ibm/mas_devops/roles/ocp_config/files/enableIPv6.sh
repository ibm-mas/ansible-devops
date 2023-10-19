#!/bin/bash

# enable ipv6
sed -i 's/disable_ipv6 = 1/disable_ipv6 = 0/g' /etc/sysctl.conf
sysctl -p

# generate new connection uuids
for FILE in $(ls /etc/sysconfig/network-scripts/ifcfg*) ; do
	sed -i '/^UUID/d' $FILE
	echo UUID=$(uuidgen) >> $FILE
done

# sync to network manager
for DEVICE in $(nmcli con show | grep -v ^NAME | awk '{print $NF}') ; do
	nmcli connection reload $DEVICE
	nmcli dev reapply $DEVICE
done
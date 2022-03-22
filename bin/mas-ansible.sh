#!/bin/bash

# !!!! INCOMPLETE / WORK IN PROGRESS / USE AT OWN RISK !!!!

# Load common functions
# -----------------------------------------------------------------------------
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. mas-common.sh

function install_dependencies_ubuntu() {
  # APT package installations
  # python3-pip is required to install additional python packages
  # ansible is required for ansible-galaxy command to be available
  sudo apt install python3-pip ansible

  # Python package installations
  python3 -m pip install ansible junit_xml pymongo xmljson kubernetes==12.0.1 openshift==0.12.1

  # Confirm versions
  python3 --version
  ansible-playbook --version
}

function build_and_install_local() {
  ansible-galaxy collection build --force
  ansible-galaxy collection install ibm-mas_devops-7.0.0.tar.gz --force
}

set_target

PLAYBOOK=$1
if [[ -z "$PLAYBOOK" ]]; then
  echo "Enter the name of a playbook to run:"
  echo " - fullstack-roks"
  echo " - lite-core-roks"
  echo " - lite-iot-roks"
  echo " - lite-manage-roks"
  echo ""
  read -p '> ' PLAYBOOK
fi

show_target
confirm "Run '$1' playbook with these settings?" || exit 0
build_and_install_local
ansible-playbook ibm/mas_devops/playbooks/$1.yml

exit 0

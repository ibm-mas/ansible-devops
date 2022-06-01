FROM registry.access.redhat.com/ubi8/python-39

# ----- Start as "default" user -----------------------------------------------
# Running as userId = default
# HOME=/opt/app-root

# ----- Switch to root user ---------------------------------------------------
# If we switch back to the "default" user then mounts in /workspace/xxx are
# not writeable, there may be a way to fix this so that we don't have to leave
# the active user as root, haven't looked into this yet.
USER root
COPY app-root/* ${HOME}/

ENV ANSIBLE_COLLECTIONS_PATH=/opt/app-root/lib64/python3.9/site-packages/ansible_collections \
    ANSIBLE_CONFIG=/opt/app-root/src/ansible.cfg

# 1. Upgrade system packages
RUN dnf update -y &&\
    dnf upgrade -y &&\
    dnf install nano -y &&\
    dnf clean all

# 2. Upgrade pip, install wheel, then install Python modules
RUN python3 -m pip install --no-cache-dir --upgrade pip wheel &&\
    python3 -m pip install --no-cache-dir -r requirements.txt

# 3. Install Ansible Collections
RUN ansible-galaxy collection install ${HOME}/ibm-mas_devops.tar.gz -p $ANSIBLE_COLLECTIONS_PATH --force &&\
    ansible-galaxy collection install -r ${HOME}/requirements.yml -p $ANSIBLE_COLLECTIONS_PATH

# 4. Set file permissions in /opt/app-root & setup symlink to our collection
RUN chmod -R ug+rwx ${HOME}/env.sh &&\
    chmod -R ug+rwx ${HOME}/.ansible &&\
    chmod a+x ${HOME}/run-playbook.sh &&\
    chmod a+x ${HOME}/run-role.sh &&\
    chmod a+x ${HOME}/clear-mustgather-workspace.sh && \
    ln -s $ANSIBLE_COLLECTIONS_PATH/ibm/mas_devops/playbooks /opt/app-root/devops

# 5. Install OpenShift CLI 4.8.35
RUN wget -q https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/4.8.35/openshift-client-linux.tar.gz &&\
    tar -zxf openshift-client-linux.tar.gz &&\
    mv oc /usr/local/bin/ &&\
    mv kubectl /usr/local/bin/ &&\
    rm -rf openshift-client-linux.tar.gz

# 6. Install IBM CLoud CLI with container-service plugin
RUN wget -q https://download.clis.cloud.ibm.com/ibm-cloud-cli/2.3.0/IBM_Cloud_CLI_2.3.0_amd64.tar.gz &&\
    tar -xvzf IBM_Cloud_CLI_2.3.0_amd64.tar.gz &&\
    mv Bluemix_CLI/bin/ibmcloud /usr/local/bin/ &&\
    rm -rf Bluemix_CLI IBM_Cloud_CLI_2.3.0_amd64.tar.gz &&\
    ibmcloud plugin repo-plugins -r 'IBM Cloud' &&\
    ibmcloud plugin install container-service

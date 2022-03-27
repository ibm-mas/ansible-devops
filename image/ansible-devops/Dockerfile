FROM registry.access.redhat.com/ubi8/python-38

# Running as userId = default
RUN echo ${HOME}

COPY requirements.yml ${HOME}/requirements.yml
COPY requirements.txt ${HOME}/requirements.txt
COPY env.sh ${HOME}/env.sh
COPY run-playbook.sh ${HOME}/run-playbook.sh
COPY save-junit-to-mongo.py ${HOME}/save-junit-to-mongo.py
COPY ansible.cfg ${HOME}/ansible.cfg
COPY ibmcloud-oc.sh ${HOME}/ibmcloud-oc.sh

# TODO: Caio, why do we switch to the root user for the rest of this Dockerfile, and why leave it as root user active at the end?
USER root

# Upgrade pip and install Python modules
RUN python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt

# Install Ansible Collections
ENV ANSIBLE_CONFIG=/opt/app-root/src/ansible.cfg

COPY ibm-mas_devops.tar.gz ${HOME}/ibm-mas_devops.tar.gz
RUN ansible-galaxy collection install ${HOME}/ibm-mas_devops.tar.gz -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections --force && \
    ansible-galaxy collection install -r ${HOME}/requirements.yml -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections
RUN chmod -R ug+rwx ${HOME}/env.sh && \
    chmod -R ug+rwx ${HOME}/.ansible && \
    chmod a+x ${HOME}/run-playbook.sh && \
    chmod a+x ${HOME}/ibmcloud-oc.sh

# Install OpenShift CLI
RUN wget -q https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz && \
    tar -xvzf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz  && \
    mv openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit/oc /usr/local/bin/  && \
    rm -rf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz

# Install IBM CLoud CLI
RUN wget -q https://download.clis.cloud.ibm.com/ibm-cloud-cli/2.3.0/IBM_Cloud_CLI_2.3.0_amd64.tar.gz &&\
    tar -xvzf IBM_Cloud_CLI_2.3.0_amd64.tar.gz && \
    mv Bluemix_CLI/bin/ibmcloud /usr/local/bin/  && \
    rm -rf Bluemix_CLI IBM_Cloud_CLI_2.3.0_amd64.tar.gz

RUN ln -s /opt/app-root/lib64/python3.8/site-packages/ansible_collections/ibm/mas_devops/playbooks /opt/app-root/playbooks

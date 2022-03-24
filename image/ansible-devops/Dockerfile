FROM registry.access.redhat.com/ubi8/python-38

RUN pip install ansible openshift jmespath
RUN echo ${HOME}

COPY requirements.yml ${HOME}/requirements.yml
COPY env.sh ${HOME}/env.sh
COPY run-playbook.sh ${HOME}/run-playbook.sh
COPY save-junit-to-mongo.py ${HOME}/save-junit-to-mongo.py
COPY ansible.cfg ${HOME}/ansible.cfg
COPY ibmcloud-oc.sh ${HOME}/ibmcloud-oc.sh

# TODO: Caio, why do we switch to the root user for the rest of this Dockerfile, and why leave it as root user active at the end?
USER root

# Install Python modules
RUN python3 -m pip install junit_xml pymongo xmljson kubernetes==12.0.1 openshift==0.12.1

# Install Ansible Collections
COPY ibm-mas_devops.tar.gz ${HOME}/ibm-mas_devops.tar.gz
RUN ansible-galaxy collection install ${HOME}/ibm-mas_devops.tar.gz -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections --force && \
    ansible-galaxy collection install -r ${HOME}/requirements.yml -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections
RUN chmod -R ug+rwx ${HOME}/env.sh && \
    chmod -R ug+rwx ${HOME}/.ansible && \
    chmod a+x ${HOME}/run-playbook.sh && \
    chmod a+x ${HOME}/ibmcloud-oc.sh

# Install OpenShift CLI 4.8.35
RUN wget -q https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/4.8.35/openshift-client-linux.tar.gz && \
    tar -zxf openshift-client-linux.tar.gz && \
    mv openshift-client-linux/oc /usr/local/bin/ && \
    mv openshift-client-linux/kubectl /usr/local/bin/ && \
    rm -rf openshift-client-linux openshift-client-linux.tar.gz

# Install IBM CLoud CLI
RUN wget -q https://download.clis.cloud.ibm.com/ibm-cloud-cli/2.3.0/IBM_Cloud_CLI_2.3.0_amd64.tar.gz &&\
    tar -xvzf IBM_Cloud_CLI_2.3.0_amd64.tar.gz && \
    mv Bluemix_CLI/bin/ibmcloud /usr/local/bin/  && \
    rm -rf Bluemix_CLI IBM_Cloud_CLI_2.3.0_amd64.tar.gz

ENV ANSIBLE_CONFIG=/opt/app-root/src/ansible.cfg

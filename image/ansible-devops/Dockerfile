FROM registry.access.redhat.com/ubi8/python-38

RUN pip install ansible openshift jmespath
RUN echo ${HOME}

COPY requirements.yml ${HOME}/requirements.yml
COPY env.sh ${HOME}/env.sh
COPY run-playbook.sh ${HOME}/run-playbook.sh
COPY save-junit-to-mongo.py ${HOME}/save-junit-to-mongo.py
COPY ansible.cfg ${HOME}/ansible.cfg

# Install IBM CLoud CLI and OC Plugin
RUN curl -fsSL https://clis.cloud.ibm.com/install/linux | sh && \
    ibmcloud plugin install container-service && \
    ibmcloud plugin list

# TODO: Caio, why do we switch to the root user for the rest of this Dockerfile, and why leave it as root user active at the end?
USER root

# Install Python modules
RUN python3 -m pip install junit_xml pymongo xmljson

# Install Ansible Collections
COPY ibm-mas_devops.tar.gz ${HOME}/ibm-mas_devops.tar.gz
RUN ansible-galaxy collection install ${HOME}/ibm-mas_devops.tar.gz -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections --force && \
    ansible-galaxy collection install -r ${HOME}/requirements.yml -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections
RUN chmod -R ug+rwx ${HOME}/env.sh && \
    chmod -R ug+rwx ${HOME}/.ansible && \
    chmod a+x ${HOME}/run-playbook.sh

# Install OpenShift CLI
RUN wget -q https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz && \
    tar -xvzf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz  && \
    mv openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit/oc /usr/local/bin/  && \
    rm -rf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz

ENV ANSIBLE_CONFIG=/opt/app-root/src/ansible.cfg

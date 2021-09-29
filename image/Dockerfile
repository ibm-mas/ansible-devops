FROM registry.access.redhat.com/ubi8/python-38

RUN pip install ansible openshift jmespath
RUN echo ${HOME}

COPY requirements.yml ${HOME}/requirements.yml
COPY env.sh ${HOME}/env.sh
COPY pipelineruns ${HOME}/pipelineruns

USER root

COPY ibm-mas_devops.tar.gz ${HOME}/ibm-mas_devops.tar.gz

RUN chmod -R ug+rwx ${HOME}/env.sh
RUN ansible-galaxy collection install ${HOME}/ibm-mas_devops.tar.gz -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections --force
RUN ansible-galaxy collection install -r ${HOME}/requirements.yml -p /opt/app-root/lib64/python3.8/site-packages/ansible_collections \
 && chmod -R ug+rwx ${HOME}/.ansible


RUN wget -q https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz \
  && tar -xvzf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz  \
  && mv openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit/oc /usr/local/bin/  \
  && rm -rf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz

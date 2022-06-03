#!/bin/bash

.PHONY: ansible-build ansible-install ansible-all docker-build docker-run docker-all clean

.DEFAULT_GOAL := ansible-all

ansible-build:
	ansible-galaxy collection build --output-path image/ansible-devops/app-root ibm/mas_devops --force
	mv image/ansible-devops/app-root/ibm-mas_devops-11.0.0.tar.gz image/ansible-devops/app-root/ibm-mas_devops.tar.gz
ansible-install:
	ansible-galaxy collection install image/ansible-devops/app-root/ibm-mas_devops.tar.gz --force
ansible-all: ansible-build ansible-install

docker-build:
	docker build -t ansible-devops:local image/ansible-devops
docker-run:
	docker run -ti ansible-devops:local
docker-all: docker-build docker-run

clean:
	rm image/ansible-devops/ibm-mas_devops.tar.gz

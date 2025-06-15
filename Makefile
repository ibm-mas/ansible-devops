#!/bin/bash

.PHONY: build build-ee install clean all

.DEFAULT_GOAL := all

build:
	ansible-galaxy collection build --output-path . ibm/mas_devops --force
install:
	ansible-galaxy collection install ibm-mas_devops-100.0.0.tar.gz --force
clean:
	rm -f ibm-mas_devops-100.0.0.tar.gz
	rm -f ibm/mas_devops/ibm-mas_devops-100.0.0.tar.gz
	rm -f ibm/mas_devops/ibm-mas_devops.tar.gz
	rm -rf target
	rm -rf context
build-ee: build
	mkdir -p ibm/mas_devops && cp ibm-mas_devops-100.0.0.tar.gz ibm/mas_devops/ibm-mas_devops.tar.gz
	export DEV_MODE="true" && source ./build/bin/build-execution-environment.sh
	ansible-builder build --prune-images --file build/ee/execution-environment.yml

all: build install

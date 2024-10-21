#!/bin/bash

.PHONY: build build-ee install clean all

.DEFAULT_GOAL := all

build:
	ansible-galaxy collection build --output-path . ibm/mas_devops --force
install:
	ansible-galaxy collection install ibm-mas_devops-100.0.0.tar.gz --force --no-deps
clean:
	rm ibm-mas_devops-100.0.0.tar.gz
build-ee:
	ansible-build --prune-images --file build/ee/execution-environment.yml

all: build install

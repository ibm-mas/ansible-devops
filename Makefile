#!/bin/bash

.PHONY: build install clean all

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

all: build install

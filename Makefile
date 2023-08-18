#!/bin/bash

.PHONY: build install clean all

.DEFAULT_GOAL := all

build:
	ansible-galaxy collection build --output-path . ibm/mas_devops --force
install:
	ansible-galaxy collection install ibm-mas_devops-17.0.0.tar.gz --force --no-deps
clean:
	rm ibm-mas_devops-17.0.0.tar.gz

all: build install

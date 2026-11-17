#!/bin/bash

.PHONY: build install clean all

.DEFAULT_GOAL := all

all: build install
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


# Python Package Documentation
# -----------------------------------------------------------------------------
.venv-docs:
	uv venv .venv-docs
	uv pip install --python .venv-docs/bin/python -q mkdocs properdocs mkdocs-carbon mkdocs-glightbox mkdocs-redirects mkdocs-gen-files

.PHONY: mkdocs-serve
mkdocs-serve: .venv-docs
	.venv-docs/bin/mkdocs serve --livereload --dev-addr localhost:9011

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


# Linting
# -----------------------------------------------------------------------------
# One-command linting of the collection: YAML (yamllint), Python (ruff) and
# Ansible content (ansible-lint). 'dev-deps' installs the toolchain and
# 'lint-collection-deps' installs the collection plus its dependencies into a
# scratch path so that ansible-lint can resolve module references.
#
# Linting is deliberately NOT part of the default 'all' target so that
# packaging is never blocked by it; it is enforced in CI instead
# (.github/workflows/lint.yml).

LINT_COLLECTIONS_PATH ?= $(HOME)/.ansible/lint-collections

.PHONY: dev-deps lint lint-python lint-yaml lint-ansible lint-collection-deps

dev-deps:
	pip install -r requirements-lint.txt

lint: lint-yaml lint-python lint-ansible

lint-yaml:
	yamllint -c yamllint.yaml ibm/mas_devops

lint-python:
	ruff check ibm/mas_devops

lint-collection-deps:
	mkdir -p $(LINT_COLLECTIONS_PATH)
	ansible-galaxy collection build --output-path /tmp ibm/mas_devops --force
	# ibm.cloudcollection (<1.52) declares requires_ansible <2.11 while this
	# collection itself requires ansible >= 2.20, so the version-mismatch check
	# is metadata-only noise here and is deliberately ignored for the lint install
	ANSIBLE_COLLECTIONS_PATH=$(LINT_COLLECTIONS_PATH) ANSIBLE_COLLECTIONS_ON_ANSIBLE_VERSION_MISMATCH=ignore \
		ansible-galaxy collection install /tmp/ibm-mas_devops-*.tar.gz -p $(LINT_COLLECTIONS_PATH) --force

lint-ansible: lint-collection-deps
	ANSIBLE_COLLECTIONS_PATH=$(LINT_COLLECTIONS_PATH) ansible-lint -c .config/ansible-lint.yml ibm/mas_devops/roles ibm/mas_devops/playbooks


# Python Package Documentation
# -----------------------------------------------------------------------------
.venv-docs:
	uv venv .venv-docs
	uv pip install --python .venv-docs/bin/python -q mkdocs properdocs mkdocs-carbon mkdocs-glightbox mkdocs-redirects mkdocs-gen-files

.PHONY: mkdocs-serve
mkdocs-serve: .venv-docs
	.venv-docs/bin/mkdocs serve --livereload --dev-addr localhost:9011

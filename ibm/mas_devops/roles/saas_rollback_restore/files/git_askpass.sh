#!/bin/sh
# GIT_ASKPASS helper: answers git's prompts from the environment so the token is never on a command line or in a URL.
case "$1" in
  Username*) printf '%s\n' "$RR_GIT_USER" ;;
  *) printf '%s\n' "$RR_GIT_TOKEN" ;;
esac

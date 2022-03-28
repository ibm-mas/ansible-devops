#!/bin/bash

if [ -e "/workspace/mustgather" ]; then
    echo "Removing previous content of /workspace/mustgather/"
    $ find /workspace/mustgather/ -mindepth 1 -delete
fi

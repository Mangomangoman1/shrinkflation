#!/usr/bin/env bash
# Daily routine (not scheduled): check, build, publish
set -e; cd "$(dirname "$0")"; python3 check.py >> check.log 2>&1; ./publish.sh

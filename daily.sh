#!/usr/bin/env bash
# Daily routine (not scheduled): check, build, publish, alert digests
set -e; cd "$(dirname "$0")"; python3 check.py >> check.log 2>&1; ./publish.sh
# Alerts: dry-run (renders to alerts/out/) unless ALERTS_SEND=1 and ALERTS_API/ALERTS_ADMIN_TOKEN are set
if [ "${ALERTS_SEND:-0}" = 1 ]; then python3 alerts/digest.py --send; else python3 alerts/digest.py; fi >> alerts.log 2>&1

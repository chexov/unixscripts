#!/bin/sh
[ $# -eq 1 ] || { echo "Usage: $0 <logs folder>"; exit 1; }
set -ue

FOLDER=$1
YYYYMMDD=$(date "+%Y-%m-%d")

find ${FOLDER}/ -type f -name \*${YYYYMMDD}\*.gz | sort | xargs -r zcat


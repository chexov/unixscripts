#!/bin/sh
[ $# -eq 2 ] || { echo "Usage: $0 s3://bucket/prefix <destination folder>"; exit 1; }
set -xue
S3PATH=$1
DEST=$2

DATE=$(date "+%Y-%m-%d")

[ -d "${DEST}" ] || mkdir "${DEST}"
LOGFILTER="${S3PATH}${DATE}"
s3cmd sync ${LOGFILTER} ${DEST} --include="*${DATE}*" --skip-existing --no-progress


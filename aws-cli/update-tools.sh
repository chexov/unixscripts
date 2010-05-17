#!/bin/sh
set -xue
s3cmd ls s3://ec2-downloads > ec2-downloads.list
cd `dirname $0`
TOOLS="AutoScaling CloudWatch ec2-ami-tools ec2-api-tools ElasticLoadBalancing"
for tool in $TOOLS; do
    key=$(egrep 'zip$' ec2-downloads.list | sort -nr | grep $tool | head -1 | awk '{ print $4}')
    s3cmd get $key --skip-existing
    b=$(basename $key)
    unzip -u $b
done
cd $OLDPWD


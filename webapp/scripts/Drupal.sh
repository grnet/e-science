#!/bin/bash

######################################
##### Functional for Drupal-7.37 #####
######################################

# $1: admin_password
CUR_DIR=`pwd`
cd;systemctl stop docker-*.scope;myvar=$(docker inspect db | grep "Id" | sed 's/[\" ,:]//g' | sed 's/Id//g');cd /var/lib/docker/containers/$myvar;/etc/init.d/docker stop;find . -name config.json -exec sed -i "s/@test123/$1/g" {{}} +;
sleep 10
/etc/init.d/docker start
sleep 10
/usr/bin/docker start db
sleep 10
/usr/bin/docker exec -d db /usr/bin/mysqladmin -u root -p@test123 password $1
/usr/bin/docker start mediawiki
sleep 10
# TODO: Change login password
docker exec -t -i db bash -c ""
sleep 5
rm -f $CUR_DIR/logs
rm -f $CUR_DIR/${BASH_SOURCE[0]}
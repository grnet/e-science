#!/bin/bash

#####################################
##### Functional for DSpace-5.3 #####
#####################################

# $1: admin_password, $2: admin_email
CUR_DIR=`pwd`
cd;systemctl stop docker-*.scope;
sleep 10
/usr/bin/docker exec -d dspace sv stop tomcat8
sleep 10
/usr/bin/docker exec -d dspace /dspace/bin/dspace create-administrator -e $2 -f changeme -l changeme -c en -p $1
sleep 10
/usr/bin/docker exec -d dspace /dspace/bin/dspace user -d -m a@b.gr
sleep 10
/usr/bin/docker exec -d dspace sv start tomcat8
sleep 10
/usr/bin/docker exec -ti dspace bash -c 'sudo -u postgres psql -U postgres -d dspace -c "alter user dspace password $1;"' -- \'$1\'
sleep 10
docker exec -ti dspace bash -c 'sed -i "s/db.password *= * *dspace/db.password=$1/g" /dspace/config/dspace.cfg' -- $1
sleep 10
/usr/bin/docker start dspace
sleep 5
rm -f $CUR_DIR/logs
rm -f $CUR_DIR/${BASH_SOURCE[0]}
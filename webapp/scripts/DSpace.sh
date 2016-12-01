#!/bin/bash

#####################################
##### Functional for DSpace-5.3 #####
#####################################

# $1: admin_password, $2: admin_email
CUR_DIR=`pwd`
WAIT_TIME=20

cd;systemctl stop docker-*.scope;
sleep $WAIT_TIME
docker exec -d dspace sv stop tomcat8
sleep $WAIT_TIME
docker exec -d dspace /dspace/bin/dspace create-administrator -e $2 -f changeme -l changeme -c en -p $1
sleep $WAIT_TIME
docker exec -d dspace /dspace/bin/dspace user -d -m a@b.gr
sleep $WAIT_TIME
docker exec -d dspace sv start tomcat8
sleep $WAIT_TIME
docker exec -ti dspace bash -c 'apt-get update; apt-get install -y sudo; sudo -u postgres psql -U postgres -d dspace -c "alter user dspace password $1;"' -- \'$1\'
sleep $WAIT_TIME
docker exec -ti dspace bash -c 'sed -i "s/db.password *= * *dspace/db.password=$1/g" /dspace/config/dspace.cfg' -- $1\
&& docker start dspace\
&& rm -f $CUR_DIR/logs\
&& rm -f $CUR_DIR/${BASH_SOURCE[0]}

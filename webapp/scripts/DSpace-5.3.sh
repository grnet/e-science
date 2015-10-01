#!/bin/bash


# $1: admin_email, $2: admin_password
cd;systemctl stop docker-*.scope;
sleep 20
/usr/bin/docker exec -d dspace sv stop tomcat8
sleep 20
/usr/bin/docker exec -d dspace /dspace/bin/dspace create-administrator -e $1 -f changeme -l changeme -c en -p $2
sleep 20
/usr/bin/docker exec -d dspace /dspace/bin/dspace user -d -m a@b.gr
sleep 20
/usr/bin/docker exec -d dspace sv start tomcat8
sleep 20
/usr/bin/docker exec -d dspace sudo -u postgres psql -U postgres -d dspace -c "alter user dspace password '$1';" -- $2
sleep 20
docker exec -ti dspace bash -c 'sed -i "s/db.password *= * *dspace/db.password=$1/g" /dspace/config/dspace.cfg' -- $2
sleep 20
/usr/bin/docker start dspace
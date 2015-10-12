#!/bin/bash

########################################
##### Functional for Redmine-3.0.4 #####
########################################

# $1: admin_password
CUR_DIR=`pwd`
WAIT_TIME=20

cd;systemctl stop docker-*.scope;myvar=$(docker inspect redmine_postgresql_1 | grep "Id" | sed 's/[\" ,:]//g' | sed 's/Id//g');cd /var/lib/docker/containers/$myvar;/etc/init.d/docker stop;find . -name config.json -exec sed -i "s/password/$1/g" {{}} +;
sleep $WAIT_TIME
/etc/init.d/docker start
sleep $WAIT_TIME
docker start redmine_postgresql_1
sleep $WAIT_TIME
docker exec -d redmine_postgresql_1 sudo -u postgres psql -U postgres -d redmine_production -c "alter user redmine password '$1';"; sed -i 's/DB_PASS=password/DB_PASS=$1/g' /usr/local/redmine/docker-compose.yml
sleep $WAIT_TIME
docker start redmine_redmine_1
sleep $WAIT_TIME
docker exec -t -i redmine_redmine_1 bash -c 'RAILS_ENV=production bin/rails runner "user = User.first ;user.password, user.password_confirmation = $1; user.save!"' -- \"$1\"\
&& rm -f $CUR_DIR/logs\
&& rm -f $CUR_DIR/${BASH_SOURCE[0]}
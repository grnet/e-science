#!/bin/bash

######################################
##### Functional for Drupal-7.37 #####
######################################

# $1: admin_password
CUR_DIR=`pwd`
WAIT_TIME=20

cd;systemctl stop docker-*.scope;myvar=$(docker inspect db | grep "Id" | sed 's/[\" ,:]//g' | sed 's/Id//g');cd /var/lib/docker/containers/$myvar;/etc/init.d/docker stop;find . -name config.json -exec sed -i "s/@test123/$1/g" {{}} +;
sleep $WAIT_TIME
/etc/init.d/docker start
sleep $WAIT_TIME
docker start db
sleep $WAIT_TIME
docker exec -d db /usr/bin/mysqladmin -u root -p@test123 password $1
sleep $WAIT_TIME
docker start drupal
sleep $WAIT_TIME
hash=$(docker exec -t -i drupal bash -c "php scripts/password-hash.sh $1 | grep hash | sed -e 's#.*hash: \\(\)#\\1#'")\
&& echo "'$hash"|sed -r 's/[$]+/\\\\\\$/g' 1> hash\
&& docker exec -t -i db bash -c "echo \"UPDATE users SET pass=`cat hash`\">mysql.sql"\
&& docker exec -t -i db bash -c "echo \"' where uid='1';\">>mysql.sql"\
&& docker exec -t -i db bash -c "mysql -p$1 drupal < mysql.sql"\
&& docker exec -t -i db bash -c "mysql -p$1 -e \"use drupal;UPDATE users SET pass=REPLACE(pass, '\n', '');\""\
&& rm -f hash; docker exec -t -i db bash -c "rm -f mysql.sql"\
&& rm -f $CUR_DIR/logs\
&& rm -f $CUR_DIR/${BASH_SOURCE[0]}
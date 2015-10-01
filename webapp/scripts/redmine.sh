#!/bin/bash

# $1: db_name, $2: default_password, $3: admin_password, $4: image
touch testfile
touch $1
cd;systemctl stop docker-*.scope;myvar=$(docker inspect $1 | grep "Id" | sed 's/[\" ,:]//g' | sed 's/Id//g');cd /var/lib/docker/containers/$myvar;/etc/init.d/docker stop;find . -name config.json -exec sed -i 's/$2/$3/g' {{}} +;/etc/init.d/docker start;/usr/bin/docker start $1
#mkdir /root/1st
sleep 20
/usr/bin/docker exec -d $1 sudo -u postgres psql -U postgres -d redmine_production -c "alter user redmine password '$3';"; sed -i 's/DB_PASS=password/DB_PASS=$3/g' /usr/local/redmine/docker-compose.yml
#mkdir /root/2nd
sleep 20
/usr/bin/docker start $4
#mkdir /root/3rd
sleep 20
docker exec -t -i redmine_redmine_1 bash -c 'RAILS_ENV=production bin/rails runner "user = User.first ;user.password, user.password_confirmation = $1; user.save!"' -- \"$3\"
#mkdir /root/last

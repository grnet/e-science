#!/bin/bash

# $1: admin_password
cd;systemctl stop docker-*.scope;myvar=$(docker inspect redmine_postgresql_1 | grep "Id" | sed 's/[\" ,:]//g' | sed 's/Id//g');cd /var/lib/docker/containers/$myvar;/etc/init.d/docker stop;find . -name config.json -exec sed -i "s/password/$1/g" {{}} +;
sleep 10
/etc/init.d/docker start
sleep 10
/usr/bin/docker start redmine_postgresql_1
sleep 10
/usr/bin/docker exec -d redmine_postgresql_1 sudo -u postgres psql -U postgres -d redmine_production -c "alter user redmine password '$1';"; sed -i 's/DB_PASS=password/DB_PASS=$1/g' /usr/local/redmine/docker-compose.yml

/usr/bin/docker start redmine_redmine_1
sleep 10
docker exec -t -i redmine_redmine_1 bash -c 'RAILS_ENV=production bin/rails runner "user = User.first ;user.password, user.password_confirmation = $1; user.save!"' -- \"$1\"

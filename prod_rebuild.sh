# run it from the project root directory with
# . prod_rebuild.sh

# settings.py
# DEBUG = False
# ~/.kamakirc make sure it points to same base_url
echo 'stop nginx if running'
sudo /etc/init.d/nginx stop
echo 'done'
echo 'stop uWSGI if running'
sudo uwsgi --stop /tmp/uwsgi.pid
sudo killall -s INT uwsgi
echo 'done'
echo 'stop celery'
celery multi stopwait celeryworker1 --loglevel=INFO --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=$HOME/logs/\%h.log
echo 'done'
echo 'stop rabbitmq'
sudo rabbitmqctl stop
echo 'done'
echo 'stop django test server if running'
sudo killall -s INT python
echo 'done'
echo 'delete *.pyc'
sudo find . -name "*.pyc" -type f -delete
echo 'done'
echo 'clean ansible files'
sudo rm ~/.ssh/known_hosts
sudo rm -rf ~/.ansible/
echo 'done'
echo 'rebuild orka'
cd orka
sudo rm -rf build/
sudo rm -rf dist/
sudo rm -rf orka.egg-info/
sudo python setup.py install
echo 'done'
echo 'clear static and media directories'
cd ../ember_django/static
sudo find . -not -name "human.txt" -not -name ".gitignore" -type f -delete
cd ../media
sudo find . -not -name "human.txt" -not -name ".gitignore" -type f -delete
echo 'done'
echo 'refresh static files'
cd ..
sudo python manage.py collectstatic --noinput
echo 'done'
echo 'restart rabbitmq'
sudo /etc/init.d/rabbitmq-server restart
echo 'done'
echo 'replicate .kamakirc'
sudo cp ~/.kamakirc /root/
echo 'done'
echo 'fix log file permissions'
sudo chown $USER:$USER $HOME/logs/*.log
echo 'done'
echo 'start celery'
celery multi start celeryworker1 --loglevel=INFO --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=$HOME/logs/\%h.log
echo 'done'
echo 'start uWSGI'
sudo uwsgi --ini $HOME/conf/uwsgi.ini
echo 'done'
echo 'start Nginx'
sudo /etc/init.d/nginx restart
echo 'done'
xdg-open http://127.0.0.1 &

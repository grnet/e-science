# run it from the project root directory with
# . debug_rebuild.sh
echo 'stop django test server'
sudo killall -s INT python
echo 'done'
echo 'delete *.pyc'
sudo find . -name "*.pyc" -type f -delete
echo 'done'
echo 'rebuild orka'
cd orka-0.1.1
sudo rm -rf build/
sudo rm -rf dist/
sudo rm -rf orka.egg-info/
sudo python setup.py install
echo 'done'
cd ../ember_django
echo 'stop uWSGI if running'
sudo killall -s INT uwsgi
echo 'done'
echo 'stop nginx if running'
sudo /etc/init.d/nginx stop
echo 'done'
echo 'stop celery'
celery multi stopwait celeryworker1 --loglevel=INFO --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=$HOME/logs/\%n\%I.log
echo 'done'
echo 'restart rabbitmq'
sudo /etc/init.d/rabbitmq-server restart
echo 'done'
echo 'start celery'
celery multi start celeryworker1 --loglevel=INFO --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=$HOME/logs/\%n\%I.log
echo 'done'
echo 'start django test server'
python manage.py runserver


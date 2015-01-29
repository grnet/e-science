# run it from the project root directory with
# . debug_rebuild.sh
echo 'rebuilding orka'
cd orka-0.1.1
sudo rm -rf build/
sudo rm -rf dist/
sudo rm -rf orka.egg-info/
sudo python setup.py install
echo 'done'
echo ''
echo 'stopping celery'
cd ../ember_django
celery multi stopwait celeryworker1 -l info --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=/home/developer/logs/\%n\%I.log
echo 'done'
echo ''
echo 'restarting rabbitmq'
sudo /etc/init.d/rabbitmq-server restart
echo 'done'
echo ''
echo 'starting celery'
celery multi start celeryworker1 -l info --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=/home/developer/logs/\%n\%I.log
echo 'done'

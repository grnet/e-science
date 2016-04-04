#!/bin/sh

USER="orka_admin"
CMD_CELERY_STOP="celery multi stopwait celeryworker1 --loglevel=WARNING --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=/home/orka_admin/logs/\%h.log"
CMD_CELERY_START="celery multi start celeryworker1 --loglevel=WARNING --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=/home/orka_admin/logs/\%h.log"
CMD_CELERY_RESTART="celery multi restart celeryworker1 --loglevel=WARNING --app=backend.celeryapp --pidfile=/tmp/\%n.pid --logfile=/home/orka_admin/logs/\%h.log"
ORKA_WEBAPP="/home/orka_admin/projects/e-science/webapp"
SERVICE=`basename $0`
PID_CELERY="/tmp/\%n.pid"


case "$1" in
    start)
        if  [ -f $PID_CELERY ]; then
            echo "Service is running"
            return 1
        fi
        cd $ORKA_WEBAPP; sudo -u $USER $CMD_CELERY_START
        ;;
    stop)
        if ! [ -f $PID_CELERY ]; then
            echo "Service not running"
            return 1
        fi
        echo "Stopping..."
        cd $ORKA_WEBAPP; sudo -u $USER $CMD_CELERY_STOP
        echo "Service Stopped"
        ;;
    restart)
        echo "Restarting..."
        cd $ORKA_WEBAPP; sudo -u $USER $CMD_CELERY_RESTART
        ;;
esac
exit 0

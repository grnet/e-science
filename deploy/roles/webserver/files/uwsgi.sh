#!/bin/sh

USER="orka_admin"
CMD_UWSGI_STOP="uwsgi --stop /tmp/uwsgi.pid"
CMD_UWSGI_START="uwsgi --ini /home/orka_admin/conf/uwsgi.ini"
ORKA_WEBAPP="/home/orka_admin/projects/e-science/webapp"
SERVICE=`basename $0`
PID_UWSGI="/tmp/uwsgi.pid"


case "$1" in
    start)
        cd $ORKA_WEBAPP; sudo -u $USER $CMD_UWSGI_START
        ;;
    stop)
        if ! [ -f $PID_UWSGI ]; then
            echo "Service not running"
            return 1
        fi
        echo "Stopping uwsgi..."
        cd $ORKA_WEBAPP; sudo -u $USER $CMD_UWSGI_STOP
        echo "Service Stopped"
        ;;
    restart)
        echo "Restarting uwsgi..."
        cd $ORKA_WEBAPP; sudo -u $USER $CMD_UWSGI_STOP
        cd $ORKA_WEBAPP; sudo -u $USER $CMD_UWSGI_START
        ;;
esac
exit 0
Running the celery worker as a daemon
--


Generally it is not mandatory, but in production you will want to run the celery worker in the background as a daemon.

Celery does not daemonize itself. so we have to use this https://github.com/celery/celery/tree/3.1/extra/generic-init.d/ directory. 

It contains generic bash init scripts for the celery worker program. These should run on Linux, FreeBSD, OpenBSD, and other Unix-like platforms. Celeryd bash script daemonizes a celery worker and the celerybeat bash script daemonizes a celery scheduler. Also, we need to create their configuration files.


For more information please check https://celery.readthedocs.org/en/latest/tutorials/daemonizing.html#daemonizing

The Webserver install playbook should be given new values from the command line for the following variables: db_user, password_db, admin_django_name, password_admin_django

Running the celery worker as a daemon
--


Generally it is not mandatory, but in production you will want to run the celery worker in the background as a daemon.

Celery does not daemonize itself. so we have to use this https://github.com/celery/celery/tree/3.1/extra/generic-init.d/ directory. 

It contains generic bash init scripts for the celery worker program. These should run on Linux, FreeBSD, OpenBSD, and other Unix-like platforms. Celeryd bash script daemonizes a celery worker and the celerybeat bash script daemonizes a celery scheduler. Also, we need to create their configuration files. 

So, if we want to run celery workers as daemons, then Webserver install.yml playbook must be run with the variable is_daemon=True.
Likewise, when a scheduler must run as a daemon, then the playbook must be executed with variable is_periodic_task=True. 


For more information please check https://celery.readthedocs.org/en/latest/tutorials/daemonizing.html#daemonizing

The following Webserver install playbook variables [password_db, db_user, db_name, admin_django_name, password_admin_django] should always be given from command line when executing the playbook. If not given, the playbook will run with the default settings.

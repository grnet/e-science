from celery.task import task
from celery import current_task
from time import sleep
from orka.create_cluster import YarnCluster


@task()
def createcluster(choices):

    new_yarn_cluster = YarnCluster(choices)
    MASTER_IP, servers = new_yarn_cluster.create_yarn_cluster()

    return MASTER_IP


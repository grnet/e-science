from celery.task import task
from celery import current_task
from time import sleep
from orka.create_cluster import YarnCluster
from orka.okeanos_utils import destroy_cluster


@task()
def create_cluster_async(choices):
    """
    Asynchronous create cluster task.
    """
    new_yarn_cluster = YarnCluster(choices)
    MASTER_IP, servers = new_yarn_cluster.create_yarn_cluster()

    return MASTER_IP

@task()
def destroy_cluster_async(master_IP, token):
    """
    Asynchronous destroy cluster task.
    """
    result = destroy_cluster(token, master_IP)
    return result


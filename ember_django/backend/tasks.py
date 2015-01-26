from celery.task import task
from celery import current_task
from backend.models import CeleryTasks
from time import sleep
from orka.create_cluster import YarnCluster


@task()
def createcluster(choices):

    new_yarn_cluster = YarnCluster(choices)
    MASTER_IP, servers = new_yarn_cluster.create_yarn_cluster()

    return MASTER_IP

@task()
def delayed_add(x, y):
    """
    dummy method to simulate a long running task
    """
    sleep(10)
    count = CeleryTasks.objects.create(count = x + y)
    return count

@task()
def progressive_increase():
    """
    progressive task for testing task feedback
    """
    for i in range(100):
        sleep(0.1)
        current_task.update_state(state="PROGRESS", meta={'current': i, 'total': 100})

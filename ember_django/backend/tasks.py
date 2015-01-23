from celeryapp import app # george: still not decided which style we're going to use: @task or @app.task
from celery.task import task
from celery import current_task
from backend.models import CeleryTasks
from time import sleep

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


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)

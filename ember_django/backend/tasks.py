from celeryapp import app
from celery.task import task
from backend.models import CeleryTasks
from time import sleep

@task()
def delayed_add(x, y):
    sleep(30)
    count = CeleryTasks.objects.create(count = x + y)
    return count

@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)

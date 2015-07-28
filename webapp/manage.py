#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script is a thin wrapper around django-admin."""

import os
import sys


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

    from djcelery.models import TaskMeta, TaskState

    TaskMeta._meta.get_field('status').max_length = 350
    TaskState._meta.get_field('state').max_length = 350

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

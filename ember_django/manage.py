#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''This script is a thin wrapper around django-admin.'''

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ember_django.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

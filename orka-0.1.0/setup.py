#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

import ez_setup
ez_setup.use_setuptools()
import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('orka/orka.py').read(),
    re.M
    ).group(1)

requires = ['kamaki==0.13rc3','paramiko','requests','PyYAML']

setup(
    name = "orka",
    packages = ["orka"],
    entry_points = {
        "console_scripts": ['orka = orka.orka:main']
        },
    version = version,
    description = "Python command line application for creating and deleting Hadoop clusters in ~okeanos.",
    install_requires = requires
    )

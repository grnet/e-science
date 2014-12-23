# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('orka/orka.py').read(),
    re.M
    ).group(1)


setup(
    name = "orka",
    packages = ["orka"],
    entry_points = {
        "console_scripts": ['orka = orka.orka:main']
        },
    version = version,
    description = "Python command line application for orka.",
    )

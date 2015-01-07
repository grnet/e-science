#!/bin/bash
apt-get update
apt-get install -y git
apt-get install -y python python-dev python-pip
pip install virtualenv
mkdir .virtualenvs
cd .virtualenvs
virtualenv --system-site-packages orkaenv
. ~/.virtualenvs/orkaenv/bin/activate
pip install ansible==1.7.2
cd
git clone https://github.com/ioannisstenos/e-science.git escience -b develop
cd escience/orka-0.1.0
python setup.py install

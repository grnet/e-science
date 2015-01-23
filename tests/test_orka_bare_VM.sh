#!/bin/bash
PROJECTGUID=$1 # project guid as found by 'kamaki project list'
GITREPO=$2 # a git repo uri
if [ $# -ne 2 ]
 then
 echo
 echo "You need to supply PROJECTGUID and GITREPO uri when calling the script"
 echo "hint: 'kamaki project list' will return project guids"
 echo
 return 1 # exit script without closing terminal if user ran it sourced: . script.sh
 exit 1 # exit if user executed it: ./script.sh
fi
kamaki server create --name testVm --flavor-id 193 --image-id e39f9997-9d67-455f-a23e-963a1f0101e3 --project-id $PROJECTGUID -p ~/.ssh/id_rsa.pub > new_vm.txt
vm=$(cat new_vm.txt | grep "SNF:fqdn:" |cut -d' ' -f2)
apass=$(cat new_vm.txt | grep "adminPass" |cut -d' ' -f2)
rm new_vm.txt
HOST="root@"$vm
echo "Wait for Vm to build..."
sleep 120
echo "Connect to VM"
echo "pass is:"$apass
ssh -o StrictHostKeyChecking=no $HOST 'apt-get update;
apt-get install -y git python python-dev python-pip;
pip install virtualenv;
mkdir .virtualenvs;
cd .virtualenvs;
virtualenv --system-site-packages orkaenv;
. ~/.virtualenvs/orkaenv/bin/activate;
pip install ansible==1.7.2;
cd ~;
git clone '$GITREPO' -b develop;
cd e-science/orka-0.1.1;
python setup.py install'

#!/bin/bash
SERVERNAME=$1 # StagingServerName
PROJECTGUID=$2 # project guid as found by 'kamaki project list' eg. 10bdefe7-07dd-43ae-a32e-d9b569640717
GITREPO=$3 # a git repo uri
GITBRANCH=$4 # a git repo branch name, tag or hash
if [ $# -lt 3 ]
  then
  echo ""
  echo "Usage:"
  echo "------"
  echo ". deploy_project.sh SERVERNAME PROJECTGUID GITREPO [GITBRANCH]"
  echo "Example:"
  echo "--------"
  echo ". deploy_project.sh Staging_ES250 \\"
  echo "10bdefe7-07dd-43ae-a32e-d9b569640717 \\"
  echo "https://github.com/ioannisstenos/e-science.git develop"
  echo "Hints:"
  echo "------"
  echo "'kamaki -k project list' will return available project info."
  echo ""
  echo "Exiting"
  echo ""
  return 1 # exit script without closing terminal if user ran it sourced: . script.sh
  exit 1 # exit if user executed it: ./script.sh
fi
START=$(date +"%s")
kamaki -k ip create --project-id=$PROJECTGUID 2>&1 | tee tmp_ip.txt
NID=$(cat tmp_ip.txt | grep "floating_network_id:" |cut -d' ' -f2)
IP=$(cat tmp_ip.txt | grep "floating_ip_address:" |cut -d' ' -f2)
rm tmp_ip.txt
sleep 5
kamaki -k server create --project-id=$PROJECTGUID --name=$SERVERNAME \
--flavor-id=145 --image-id=643bf714-7c92-412d-92bb-013dc37efec9 \
--network=$NID,$IP \
-p ~/.ssh/id_rsa.pub,/root/.ssh/authorized_keys,root,root,0700 --wait 2>&1 | tee tmp_vm.txt
VM=$(cat tmp_vm.txt | grep "SNF:fqdn:" |cut -d' ' -f2)
APASS=$(cat tmp_vm.txt | grep "adminPass" |cut -d' ' -f2)
rm tmp_vm.txt
HOST="root@"$VM
echo "Waiting a minute for VM to be reachable..."
sleep 60
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
'apt-get update;
apt-get install -y git python python-dev python-pip;
pip install ansible==1.7.2;
pip install kamaki==0.13.1;
exit'
echo "Information" > $SERVERNAME.txt
echo "===========" >> $SERVERNAME.txt
echo "~okeanos VM Name: $SERVERNAME" >> $SERVERNAME.txt
echo "User: root" >> $SERVERNAME.txt
echo "FQDN: $VM" >> $SERVERNAME.txt
echo "IP: $IP" >> $SERVERNAME.txt
echo "Admin pass: $APASS" >> $SERVERNAME.txt
END=$(date +"%s")
DIFF=$(($END-$START))
echo ""
echo "VM Created in:"
date -u -d @"$DIFF" +'%-Mm %-Ss'
echo "[webserver]" > ansible_hosts
echo "$VM ansible_ssh_host=$IP" >> ansible_hosts
echo "[webserver:vars]" >> ansible_hosts
echo "escience_repo=$GITREPO" >> ansible_hosts
echo "escience_version=$GITBRANCH" >> ansible_hosts
echo "[defaults]" > ansible.cfg
echo "host_key_checking = False" >> ansible.cfg
echo ""
echo "Setting up Servers (Ansible)"
ansible-playbook -i ansible_hosts deploy.yml -e "choose_role=webserver create_orka_admin=True"
END=$(date +"%s")
DIFF=$(($END-$START))
echo ""
echo "ALL Done in:"
date -u -d @"$DIFF" +'%-Mm %-Ss'
echo "Info saved in $SERVERNAME.txt in current directory."
URL="http://$IP"
xdg-open $URL &
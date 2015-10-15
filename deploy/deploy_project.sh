#!/bin/bash
SERVERNAME=$1 # StagingServerName
PROJECTGUID=$2 # project guid as found by 'kamaki project list'
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
	echo ". deploy_project.sh ES250 \\"
	echo "10bfake7-07dd-43ae-a32e-placeholder7 \\"
	echo "https://github.com/grnet/e-science.git develop"
	echo "Hints:"
	echo "------"
	echo "'kamaki -k project list' will return available project info."
	echo ""
	echo "Exiting"
	echo ""
	# terminate script without closing terminal if user ran it sourced: . script.sh
	# exit if user executed it: ./script.sh
	return 1 2>/dev/null || exit 1
fi
START=$(date +"%s")
kamaki -k ip create --project-id=$PROJECTGUID 2>&1 | tee tmp_ip.txt
NID=$(cat tmp_ip.txt | grep "floating_network_id:" |cut -d' ' -f2)
IP=$(cat tmp_ip.txt | grep "floating_ip_address:" |cut -d' ' -f2)
rm -f tmp_ip.txt
if [ -z "$IP" ] 
 then
	echo "Couldn't get a floating IP"
	echo "Exiting"
	echo ""
	return 1 2>/dev/null || exit 1
fi
sleep 5
kamaki -k server create --project-id=$PROJECTGUID --name=$SERVERNAME \
--flavor-id=145 --image-id=d3782488-1b6d-479d-8b9b-363494064c52 \
--network=$NID,$IP \
-p ~/.ssh/id_rsa.pub,/root/.ssh/authorized_keys,root,root,0700 --wait 2>&1 | tee tmp_vm.txt
VM=$(cat tmp_vm.txt | grep "SNF:fqdn:" |cut -d' ' -f2)
APASS=$(cat tmp_vm.txt | grep "adminPass" |cut -d' ' -f2)
rm -f tmp_vm.txt
if [ -z "$VM" ] 
 then
	echo "Couldn't create a VM"
	echo "Exiting"
	echo ""
	return 1 2>/dev/null || exit 1
fi
HOST="root@"$VM
echo "Waiting a minute for VM to be reachable..."
sleep 60
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
'apt-get install -y python;
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
ansible-playbook -i ansible_hosts staging.yml -e "choose_role=webserver create_orka_admin=True" -t preimage #,postimage
END=$(date +"%s")
DIFF=$(($END-$START))
echo ""
echo "ALL Done in:"
date -u -d @"$DIFF" +'%-Mm %-Ss'
<<<<<<< HEAD
echo "Info saved in $SERVERNAME.txt in current directory."
URL="http://$IP"
xdg-open $URL &

=======
echo "Info saved in $SERVERNAME.txt in current directory."
>>>>>>> 4deccfc205e866fe4d8fbe06ad694598ab652660

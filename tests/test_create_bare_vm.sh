#!/bin/bash
kamaki server create --name testVm --flavor-id 193 --image-id e39f9997-9d67-455f-a23e-963a1f0101e3 --project-id <project id> -p ~/.ssh/id_rsa.pub > new_vm.txt
vm=$(cat new_vm.txt | grep "SNF:fqdn:" |cut -d' ' -f2)
apass=$(cat new_vm.txt | grep "adminPass" |cut -d' ' -f2)
rm new_vm.txt
HOST="root@"$vm
echo "Wait for Vm to be build..."
sleep 120
echo "Conect to VM"
echo "pass is:"$apass
ssh -o StrictHostKeyChecking=no $HOST 

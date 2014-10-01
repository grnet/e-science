e-science
=========

How to run script:

python script_name.py "arguments"

    arguments: 
      --list_of_hosts='List_of_hosts is the list that has every fqdn and private ip of the virtual machines',
      --public_ip="it is the ipv4 of the master node" 
      --cluster_name='it is the name of the cluster'

example

    python script_name.py --list_of_hosts=[] --public_ip= 1.2.3.4  --cluster_name='cluster'

e-science
=========

How to run scripts:

Create
```sh
    python create_cluster.py --name=Test_CLI --cluster_size=3 --cpu_master=4 --ram_master=2048 --disk_master=5 
    --cpu_slave=2 --ram_slave=1024 --disk_slave=5 --disk_template=ext_vlmc --image='Debian Base' 
    --token={user token} --logging=report --project_name={name of the project}
```
Check
```sh
    python check_user_quota.py --token={user token} --project_name={name of the project}
```
Delete
```sh
    python destroy_okeanos_cluster.py --token={user token} --master_ip={master ip}
```
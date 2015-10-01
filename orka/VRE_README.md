#Virtual Research Environment (VRE) Images

orka vre commands are used to manage VM appliances which cover a wide range of open-software stacks needed for everyday Research and Academic activities. These images are ~okeanos pre-cooked VMs created with Docker.

##"vre create" command

Required positional arguments for vre create command:

    name: "name of the VRE server",
    cpu: "number of CPU cores of VRE server",
    ram: "ram in MiB of VRE server",
    disk: "hard drive in GiB of VRE server",
    disk_template: "Standard or Archipelago",
    project_name: "name of a ~okeanos project, to pull resources from",
    image: "name of VRE image"
    
Optional arguments for vre create command:

    admin_password: "Admin password for VRE servers. Default is auto-generated",
    admin_email: "Admin email for VRE DSpace image. Default is admin@dspace.gr"
    
 **admin_password must contain only uppercase and lowercase letters and numbers and be at least eight characters long**.

### {orka vre create} command examples

example for orka vre create with Drupal and DSpace images:

    orka vre create Drupal_Test 2 2048 20 Standard <project_name> Drupal-7.37 --admin_password=My21PaSswOrd
    orka vre create DSpace_Test 2 2048 20 Standard <project_name> DSpace-5.3 --admin_password=sOmEoTheRPassWorD --admin_email=mymail@gmail.com
    
##"vre destroy" command

Required positional arguments for vre destroy command:

    server_id: "VRE Server id in e-science database"
(server_id is returned after creation of VRE server and will be added later to **orka vre list** command)

### {orka vre destroy} command examples

example for orka vre destroy:

    orka vre destroy <server_id>
    
## "vre images" command

vre images command has no required positional or optional arguments.

### {orka vre images} command example

example for listing available VRE images and their pithos uuid values

    orka vre images
## "vre list" command
Optional arguments for vre list command:

    --status="Choose from:ACTIVE, PENDING, DESTROYED (case insensitive, shows only VRE servers with specified status)"
    --verbose (outputs full VRE server details. Default: off)
vre list command has no required positional arguments.

### {orka vre list} command example

example for listing user VRE servers:

	orka vre list --status=active --verbose

## General Docker Info

VRE images are built using widely used Docker images pulled from http://hub.docker.com Repository. Components (i.e. Docker layers) inside the VM are not directly accessible from the Linux host's regular filesystem.
In general, in order to access a docker container's bash, type:

    docker exec -t -i <container_name> bash
For example, to access the mysql layer (db) in the **Drupal** or **Mediawiki** image:

    docker exec -t -i db bash
    mysql -p

and give the admin_password when prompted for password.

In order to change the mysql root password, type:

    docker exec -t -i db bash -c "mysqladmin -p<old_password> password <new_password>"
then, stop the docker service:

    service docker stop
and find the **config.json** of the corresponding container, open the file and change the variable MYSQL_ROOT_PASSWORD = *new_password*

To find the **config.json** of the mysql (named db) container:

    myvar=$(docker inspect db | grep "Id" | sed 's/[" ,:]//g' | sed 's/Id//g')
    cd /var/lib/docker/containers/$myvar

Finally, start docker and containers, as the drupal example below:

    service docker start
    docker start db
    docker start drupal
In case of **Redmine** image, to access the postgresql database:

    docker exec -t -i redmine_postgresql_1 bash
    psql -U redmine -d redmine_production -h localhost
and give the admin_password when prompt for password.

In order to change the postgresql password, type:

    docker exec -t -i redmine_postgresql_1 bash
enter the postgresql prompt:

    sudo -u postgres psql -U postgres -d redmine_production
and change the password:

    alter user redmine password '<new_password>';

then, stop the docker service:

    service docker stop
and find the **config.json** of the corresponding container, open the file and change the variable DB_PASS = *new_password*. The same should be done for the file /usr/local/redmine/docker-compose.yml

To find the **config.json** of the postgresql (named redmine_postgresql_1) container:

    myvar=$(docker inspect redmine_postgresql_1 | grep "Id" | sed 's/[" ,:]//g' | sed 's/Id//g')
    cd /var/lib/docker/containers/$myvar

Finally, start docker and containers:

    service docker start
    docker start redmine_postgresql_1
    docker start redmine_redmine_1
    
For **DSpace image**, the database resides in the same container with DSpace.
So, in order for the postgresql database to be accessed, the following commands are needed:

    docker exec -t -i dspace bash
    psql -U dspace -d dspace -h localhost
    
and give the admin_password. If the postgresql dspace password is changed, it must be also changed in the file /dspace/config/dspace.cfg, which is inside the DSpace container.

The entry db.password=<old_password> inside the dspace.cfg file must be changed to reflect the change in postgresql. After the change, stop and start the docker dspace container. It needs around 4 minutes to be up and running, before DSpace URLs can be accessed.

In case of **BigBlueButton**, there is no admin account and no database. The recommended minimum hardware requirements are: 4 CPUs and 4 GiB ram.

## Access VRE servers

| VRE image   | Access URL
|------------ |:---
| Drupal      | *VRE server IP*
| Mediawiki   | *VRE server IP*
| Redmine     | *VRE server IP*
| DSpace      | *VRE server IP*`:8080/jspui` && *VRE server IP*`:8080/xmlui`
| BigBlueButton | *VRE server IP*

## Backup and Restore procedure of docker container's directories and database

For example, in **DSpace image** case:

First, determine which directories are needed to be backed up.

    - installation directory
    - web deployment directory
        - In our case it resides inside the installation directory.

Next, open bash inside the DSpace container:

    docker exec -it dspace bash

**DSpace installation folder backup**

    nano /dspace/config/dspace.cfg
        #find line: <dspace.dir = {{dspace installation folder}}>
        #here it is /dspace
    cd
        #backup will be saved on your (root) home directory
    tar zcC /dspace > dspace_installation-backup-$(date +%Y-%m-%d).tar.gz .

**DSpace installation folder restore**

    cd
    tar zxC / -f dspace_installation-backup-{{select date}}.tar.gz

**DSpace db backup**

    cd
    #store password, so that dump doesn't ask for password for each database dumped
        nano .pgpass
            localhost:*:*:dspace:dspace
        chmod 600 .pgpass
    pg_dump -Fc dspace -U dspace -h localhost > dspace_db-backup-$(date +%Y-%m-%d).bak

**DSpace db restore**

    cd 
    pg_restore -Fc dspace_db-backup-{{select date}}.bak -U dspace -h localhost

**Docker installation directories**

| VRE image   | Installation directory
|------------ |:---------------------
| Drupal      | */var/www/html*
| Mediawiki   | */var/www/html*
| Redmine     | */home/redmine*
| DSpace      | */dspace*
| BigBlueButton | */var/lib/tomcat6/webapps*

## Useful Docker links:

https://www.docker.com/

https://docs.docker.com/articles/basics/

https://docs.docker.com/reference/commandline/exec/

## Getting help

Also, with

    orka vre -h

helpful information about the orka vre CLI is depicted.

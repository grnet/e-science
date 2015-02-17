## Staging orka
A collection of bash and ansible scripts have been assembled in `<project_root>/deploy` to facilitate the deployment of a specific version of the application to a staging environment for testing.  
The staging environment consists of a standalone Virtual Machine running a release configuration with the Nginx-uWSGI-Postgres stack, serving the application from a public IP.

### Prerequisites
Running the deployment script assumes [Kamaki](https://www.synnefo.org/docs/kamaki/latest/index.html) installed and an [~okeanos](https://accounts.okeanos.grnet.gr/ui/api_access) API access token available.

### Running the deployment script
1. Checkout or clone a recent version of the [e-science](https://github.com/grnet/e-science/tree/develop) project.
2. Open a terminal at `e-science/deploy/`
3. Run the deploy_project.sh script in source mode with 
```shell
. deploy_project.sh SERVERNAME PROJECTGUID GITREPO [VERSION]
```  
  _Running the script without any parameters will output brief help and an example._
  
#### Script arguments
- SERVERNAME: Arbitrary user provided name of the Virtual Machine hosting the application.
- PROJECTGUID: The GUID part of a project the user has resources on, as found by querying project info with kamaki.
```shell
kamaki -k project list
```
- GITREPO: URI of a git repository hosting the application files.
- VERSION: (Optional) `Branch`, `Tag` or `commit hash` of GITREPO. If omitted `origin` is used.

##### Example
```shell
. deploy_project.sh ES250 10bfake7-07dd-43ae-a32e-placeholder7 https://github.com/grnet/e-science.git develop
```

### Results, Script Feedback
After running the command and if all resources are available the script will work unattended for 10-15 minutes.  
At the end it will attempt to open the newly created public IP hosting the application in the users browser.  
All the Virtual Machine info necessary for remoting into the staging environment or open the application URL at a later date are also written into SERVERNAME.txt at the current directory.  
_If at any point the script cannot proceed (lack of resources or other error) it will exit._

### Miscellaneous Info
- Changes to the webstack configuration files (nginx, uwsgi etc) are not under source control so if something significant changes in how the stack is configured the deploy package configuration files used by ansible will also have to be updated.
- If the user has configured their ~/.kamakirc with `ignore_ssl = on` option or have their ssl CA certificates installed they will not need to run kamaki commands with -k.


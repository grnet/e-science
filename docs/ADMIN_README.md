#Administrator's Guide

Instructions for the application admin on how to:

* configure application settings, 
* add Orka and VRE Images, 
* add VRE image categories, 
* add Public News, 
* change database and login passwords for VRE servers

First, you need to login into the e-Science Administration interface. In the E-Science section choose to **edit one of the below options only**.

## Application Settings

In order to change the (Cluster or VRE) small, medium and large **flavors**, which are in their create pages, edit the flavor that needs to be changed and in the field *Property Value* replace with the desirable number. 
*Do not change the alphabetic characters or add any attributes in the json object.*
Also, the **storage** templates can be changed, according to those provided by ~okeanos.

## Orka Image Categories

In order to add a new Orka Image Category, press the button *Add orka image category* and complete the field with the new category name. If for the creation of the new orka image is necessary to use ansible, then complete the fields below, starting with the appropriate ansible *role* and *tags* keywords and continuing to the other field for the action tags, all in json format. To rename an Orka Image Category, choose the desired one and replace the field *OrkaImageCategory name* with the new name.

## Orka Images

If a new Orka Image is about to be added in the application, then in this section press the button *Add Orka Image* and add the pithos image name, the pithos image uuid and choose from the dropdown menu the image category it belongs. The rest fields are optional. You can add any information about the image's components. Also, if the image has CPU, RAM or storage disk minimum requirements, then in the field *Image min reqs* add them with the respective keywords: cpu, ram, disk.
For example if the minimum RAM requirement for an Orka image is at least 2048MiB, then input:

    Image min reqs: {"ram":2048}

To provide a space for user's common questions, you can add helpful links in the field *Image faq links* in key-value pairs (json format), where key is the information message and value is the link to redirect to.

In case the Orka image has extra fields, then complete (**not in json format**) in the field *Image init extra*. For more than one extra fields, separate them by commas.

If the Orka image's access URL requires a port, then complete (**not in json format**) the field *Image access url* by placing the port or port/path respectively to the case.
For example, if the access URL is http://< IP >:8088/cluster, then:

    Image access url: 8088/cluster

To update an Orka Image's information, choose the desired one and do the necessary changes.

## Public News Items

In order to add news in the homepage of the application, press the button *Add Public News Item* and complete the date/time of the news, as well as the respective text.

## VRE Image Categories

In order to add a new VRE Image Category, press the button *Add vre image category* and complete the field with the new category name. To rename a VRE Image Category, choose the desired one and replace the field *VreImageCategory name* with the new name.

## VRE Images

In order to add a new VRE Image, press the button *Add VRE Image* and add the pithos image name, the pithos image uuid and choose from the dropdown menu the image category. Optionally you can add any image components. 
Also, if the image has CPU, RAM or storage disk minimum requirements, then in the field *Image min reqs* add them with the respective keywords: cpu, ram, disk.
For example if the minimum requirements are at least 2 Cores and 2048MiB RAM for a VRE image, then input:

    Image min reqs: {"cpu":2,"ram":2048}
    
To provide a space for user's common questions, you can add helpful links in the field *Image faq links* in key-value pairs (json format), where key is the information message and value is the link to redirect to.

In case the VRE image has extra fields, such as admin_password, then complete (**not in json format**) in the field *Image init extra*. For more than one extra fields, separate them by commas.

If the VRE image's access URL requires a port, then complete (**not in json format**) the field *Image access url* by placing the port/path. In case of more than one access URLs are needed, separate them by commas.
For example, if the access URL is https://< IP >:8080/xmlui, then:

    Image access url: 8080/xmlui

If the VRE image requires a shell script to start its services and change the database and the admin password, then *requires_script* field should be checked.Otherwise, it should be unchecked, e.g. BigBlueButton. If the field is checked, the app expects to find a script in "e-science/webapp/scripts" folder.

## Change database and login passwords for VREs

In the "e-science/webapp/scripts" folder there are several shell scripts that change the VRE default database and login passwords. 
**In case a new VRE image has been added and the *requires_script* field is checked, then the corresponding script filename should be exactly the same as the name of the image (case sensitive) minus the version.**


It is possible to change the passwords of a VRE that has already its passwords changed from default (after it has been created). Replace the old default password to the corresponding script with the new given (before the creation) "admin password". Then copy the script to the VRE server and execute it by giving as parameter the new admin password. 
Example of executing Drupal script:

    . Drupal.sh {{password}}

In case of DSpace, also replace the default email and execute the script by giving as parameters the new admin password and the new admin email. 
Example of executing DSpace script:

    . DSpace.sh {{password}} {{email@example.com}}
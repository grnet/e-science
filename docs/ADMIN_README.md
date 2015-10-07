#Administrator Guide

Instructions for application admin on how to configure application settings, add Orka and VRE Images, add VRE image categories, add Public News, change database and login passwords to VREs.

Login into the GRNET e-Science Administration interface. In the E-Science section choose to **edit one of the below options only**.

## Application Settings

In order to change the Cluster or VRE small, medium and large **flavors**, which are in their create pages, edit the flavor that needs to be changed and in the field *Property Value* replace with the desirable number. 
*Do not change the alphabetic characters or add any attributes in the json object.*
Also, the **storage** templates can be changed, according to those provided by ~okeanos.

## Orka Images

If a new Orka Image is about to be added in the application, then in this section press the button *Add Orka Image* and add the pithos image name, the pithos image uuid and optionally any image components in the fields shown. To update an Orka Image's information, choose the desired one and do the changes needed.

## Public News Items

In order to add news in the homepage of the application press in this section the button *Add Public News Item* and complete the date and time of the news creation and the text to be shown.

## VRE Image Categories

In order to add a new VRE Image Category, press the button *Add vre image category* and complete the field with the new category name. To rename a VRE Image Category, choose the desired one and replace the field *VreImageCategory name* with the new name.

## VRE Images

In order to add a new VRE Image, press the button *Add VRE Image* and add the pithos image name, the pithos image uuid and choose from the dropdown menu the image category. It is optional to add any image components. 
Also, if the image has CPU, RAM or storage disk minimum requirements, then in the field *Image min reqs* add them with the keywords cpu, ram, disk.
For example if the minimum requirements are at least 2 cpu and 2048MiB ram for a VRE image, then:

	Image min reqs: {"cpu":2,"ram":2048}
	
To prevent the users from asking common questions, it is possible to add helpful links in the field *Image faq links* in key-value pairs (json format), where key is the information message and value is the link to redirect to.
In case the VRE image has extra fields, such as admin_password, then complete (**not in json format**) the field *Image init extra*. For more than one extra fields, separate them by commas.
If the VRE image's access url is not only its IP address, then complete (**not in json format**) the field *Image access url* by placing the port/path. In case of more than one access urls, separate them by commas.
For example, if the access url is https://< IP >:8080/xmlui, then:

	Image access url: 8080/xmlui

## Change database and login passwords to VREs

In the folder e-science/webapp/scripts there are several shell scripts that change the VRE default database and login passwords. 
**In case a new VRE image has been added, then the corresponding script should be named with the alphabetic characters of the name of the image (case sensitive).**

It is possible to change the passwords of a VRE that has already its passwords changed from default (after creation). Replace the old default password to the corresponding script with the new given (before the creation) "admin password". Then copy to the VRE server the script and execute it giving as parameter the new admin password. 
Example of executing Drupal script:

	. Drupal.sh password

In case of DSpace, also replace the default email and execute the script giving as parameters the new admin password and the new admin email. 
Example of executing DSpace script:

	. DSpace.sh password email@example.com

#Create developer's environment

##Table of Context
1. General Information
2. Installation Procedures
3. Credentials
4. Initial configuration of new Debian image

##General Information
* Virtual Box: 4.3.12-93773 (with Oracle_VM_VirtualBox_Extension_Pack-4.3.12-93733)
* OS:  Debian 7.5.0 amd64 (64bits)
* Ram: 1.4GB
* Disk: 8GB

##Installation procedures
* Start VirtualBox 
* Select Machine | New from the menu 
  1.	Name and operating system: Name: Debian-x64 | Type: Linux | Version: Debian (64 bit), click Next
  2.	Memory size: 1.4GB, click next
  3.	Hard drive
      * Choose Create a virtual hard drive now, click Create
      * Choose VDI (VirtualBox Disk Image) in Hard drive file type, click Next
      * Dynamically allocated in Storage on physical hard drive, click Next
      * File location and size: Select a path for the virtual disk image & 8 GB for size
      * Click Create
  4. Select Debian-x64 | Settings 
      * Select Display | Video Memory: 128 MB & Disable 3D Acceleration
      * Select Storage | Controller SATA | Debian-x64.vdi | Attributes | Hard Disk: Setup the virtual hard disk (icon) |  Choose a virtual hard disk file | Find and select the VDI image, click Open, click OK
* Start the Virtual Machine

> > NOTE: If the Debian (64 bit) choice is not available in Version setting of Name and operating system Tab, make sure that Intel Virtualization Technology (IVT) is enabled in the host UEFI / BIOS.

##Credentials
* User: developer
* User password: escience
* Root password: developer

##Initial configuration of new Debian image
###Enabling root GUI login
Comment out the following line in gdm3 file

      su root
      vi /etc/pam.d/gdm3
      "#auth required pam_succeed_if.so user != root quiet_success"

###Improve vi editor

      apt-get install vim

###Installation of curl and g++

      apt-get install curl
      apt-get install g++
    
###Change the keyboard layout
* Applications->System Tools->Preferences->System Settings
* In Region and Language ->Layouts tab and add Greek and English (US) and remove English(UK).

###Install Kamaki 
* instructions based on Kamaki 0.12.9 documentation | https://www.synnefo.org/docs/kamaki/latest/installation.html


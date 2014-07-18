#Create developer's environment

##Table of Context
1. General Information
2. Installation Procedures
3. Credentials

##General Information
* Virtual Box: 4.3.12-93773 (with Oracle_VM_VirtualBox_Extension_Pack-4.3.12-93733)
* OS:  Debian 7.5.0 amd64 (64bits)
* Ram: 1.4GB
* Disk: 8GB


##Installation procedures
* Start VirtualBox 
* Select Machine | New from the menu 
  1.	Name and operating system. Name: Debian-x64 | Type: Linux | Version: Debian (64 bit), click next
  4.	Memory size: 1.4GB, click next
  5.	Hard drive
      * Choose Create a virtual hard drive now
      * Click Create
      * Choose VDI (VirtualBox Disk Image)
      * Click Create 
      * File allocation and size: Select a path for the virtual disk image & Select 8 GB for size
      * Click Create
  6. Select Debian-x64 | Settings 
  7. Select Display | Video & Bump up the video memory to 128 MB & Do not check Enable 3D Acceleration
  8. Select Storage | Controller SATA 
  9. Click on the little blue icon next to hard disk: SATA port |  Choose a virtual hard disk
      * Find and select the VDI image downloaded from pithos
      * Click OK
OR
      * Right click Controller SATA | add hard disk | choose existing disk | Find and select the VDI image downloaded from pithos

  10. Start the Virtual Machine



  
> > NOTE: If the Debian (64 bit) choice is not available, make sure Intel Virtualization Technology is enabled in the host UEFI / BIOS.







##Credentials
Root password: developer
User: developer
User password: escience



##
Improves vi editor: Apt-get install vim
Installs the curl command we need later: Apt-get install curl
Apt-get install g++


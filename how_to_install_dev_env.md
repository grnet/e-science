#Create developer's environment

##Table of Contents
1. General Information
2. Installation Procedures
3. Credentials

##General Information
* Virtual Box: 4.3.16-95972
* OS:  Debian 7.6.0 amd64 (64bits)
* Ram: 1.0GB
* Disk: 20GB

##Installation procedures
* Start VirtualBox 
* Select Machine | New from the menu 
  1.	Name and operating system: Name: Debian-x64 | Type: Linux | Version: Debian (64 bit), click Next
  2.	Memory size: 1.0GB, click next
  3.	Hard drive
      * Choose Create a virtual hard drive now, click Create
      * Choose VDI (VirtualBox Disk Image) in Hard drive file type, click Next
      * Dynamically allocated in Storage on physical hard drive, click Next
      * File location and size: Select a path for the virtual disk image & 20 GB for size
      * Click Create
  4. Select Debian-x64 | Settings 
      * Select Display | Video Memory: 128 MB & Disable 3D Acceleration
      * Select Storage | Controller SATA | Debian_Golden-x64.vdi | Attributes | Hard Disk: Setup the virtual hard disk (icon) |  Choose a virtual hard disk file | Find and select the VDI image, click Open, click OK
* Start the Virtual Machine

> > NOTE: If the Debian (64 bit) choice is not available in Version setting of Name and operating system Tab, make sure that Intel Virtualization Technology (IVT) is enabled in the host UEFI / BIOS.

##Credentials
* User: developer
* Password: escience

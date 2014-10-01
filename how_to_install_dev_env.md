#Create developer's environment

##Table of Contents
1. General Information
2. Installation Procedures
3. Credentials
4. Git Configuration

##General Information
* Virtual Box: 4.3.16-95972
* OS:  Debian 7.6.0 amd64 (64bits)
* Ram: 1.0GB
* Disk: 20GB
* Software components (pre-installed): Oracle Java 1.7, pip 1.1, git 1.7.10.4, Kamaki 0.13rc3, Ansible 1.6.6, Python 2.7.3, Celery 3.1.15, PostgreSql 9.1.13, Django 1.7, RabbitMQ 2.8.4, PHP5, Eclipse luna 4.4, Skype 4.3.0.37

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

##Git Configuration
Each user should define his own personal info for git
(see: http://git-scm.com/book/en/Getting-Started-First-Time-Git-Setup)

    git config --global user.name [your username]
    git config --global user.email [your email]

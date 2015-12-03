![alt text](http://grnet.github.io/grnet-media-pack/grnet/logos/grnet_logo_en.svg "GRNET Logo") 

[![Build Status](https://travis-ci.org/grnet/e-science.svg?branch=develop)](https://travis-ci.org/grnet/e-science)
# GRNET eScience platform
eScience is a cloud-based integrated service platform for big data analytics offered by GRNET and the associated [~okeanos](http://okeanos.grnet.gr) IaaS.

## Orka overview
Currently the codenamed *orka* (ver 0.3.0) CLI and Web interfaces enable ~okeanos users to create Hadoop 2.x \(YARN\) multi-node clusters (http://apache.hadoop.org) in order to run their big data algorithms. Researchers, university students and teachers can fully exploit the MapReduce (as well as others) programming paradigm without wasting time and resources in hardware maintenance, software setup, etc.

## Features
Orka software platform provides the following functionality to ~okeanos users:

- Create YARN clusters with selected flavors for master and slave nodes
- Choose from a number of pre-cooked images: Hadoop Core, Cloudera, Hue, and a consolidated image with Pig, Hive, HBase, Oozie, Spark, Flume
- Run your workflows with Oozie
- Stream external data into HDFS with Flume
- Manage your cluster (Start, Stop, Format, Destroy)
- Scale your cluster  (Add, Remove nodes)
- Use [Pithos+](http://pithos.okeanos.grnet.gr) as a storage backend, run your MapReduce algorithms with input and output directly from/to Pithos+ files
- Create Virtual Research Environment (VRE) servers from a range of widely known open-source software for wiki, portal, project management, teleconference, digital repositories.
- Save your experiment (cluster metadata and scripts) and replay your algorithm later with the same or different parameters
- Create your own pre-cooked images, and add them to your own orka server's dropdown list of availabe images
- CLI and GUI to perform all of the above
 

## Architecture
On a high-level, Orka is being developed in a REST-API architectural fashion. Each client (CLI or Web) communicates with the orka server backend through REST calls (depicted in this [schema](docs/orka_arch_diagram.png)).

## Installation procedure
Detailed information about installing and running your own local orka server on Debian OS is located in orka/README.md.

### Use it at your terminal
Running orka commands from your terminal is documented in orka/CLI_README.md. 

### GUI access
After creating a local orka server, login to create Hadoop-YARN clusters and VRE servers with your ~okeanos token. Note: You need at least 2 VMs in an ~okeanos project to build the minimum YARN cluster.

### ~Orka portal
Useful information about orka features, news, media content, and installation steps can be found at the [orka portal](https://escience.grnet.gr)

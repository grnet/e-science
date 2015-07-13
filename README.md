![alt text](http://grnet.github.io/grnet-media-pack/grnet/logos/grnet_logo_en.svg "GRNET Logo") 

[![Build Status](https://travis-ci.org/grnet/e-science.svg?branch=develop)](https://travis-ci.org/grnet/e-science)
# GRNET eScience
eScience is a cloud-based integrated service platform for big data analytics offered by GRNET and the associated [~okeanos](http://okeanos.grnet.gr) IaaS.

## Orka package
Currently the codenamed *orka* (ver 0.2.0) CLI and Web interfaces enable ~okeanos users to create Hadoop 2.x \(YARN\) multi-node clusters (http://apache.hadoop.org) in order to run their big data algorithms. Researchers, university students and teachers can fully exploit the MapReduce (as well as others) programming paradigm without wasting time and resources in hardware maintenance, software setup, etc.

## Features
Orka software platform provides the following functionality to ~okeanos users:
- Create clusters with selected flavors for master and slave nodes
- Choose from a number of pre-cooked images: Hadoop Core, Cloudera, Hue, and a consolidated image with Pig, Hive, HBase, Oozie, Spark, Flume
- Run your workflows with Oozie
- Manage your cluster (Start, Stop, Format, Destroy)
- Use [Pithos+](http://pithos.okeanos.grnet.gr) as a storage backend, input and output directly from/to Pithos+ files
- CLI and GUI to perform all of the above
 
## Future
eScience software adopts the agile methodology. At the end of each development cycle (aka sprint) a new shippable software increment is delivered. Features to be included in future orka  versions include:

- submit jobs to cluster
- save your jobs (with metadata) to replay your algorithm later
- documentation for various pre-cooked images
- provide your own configuration options

## Architecture
On a high-level, Orka is being developed in a REST-API architectural fashion. Each client (CLI or Web) communicates with the eScience backend through REST calls. [schema](docs/orka_arch_diagram.png)

## Use it at your terminal
Detailed information about installing and running orka on Debian OS is located in orka/README.md. Installation steps on other Linux distribution may differ, and may need further adjustments.

## Homepage URL
Login to (http://escience.grnet.gr) to create Hadoop clusters with your ~okeanos token. You need at least 2 VMs in an ~okeanos project to build the minimum YARN cluster.


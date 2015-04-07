![alt text](http://grnet.github.io/grnet-media-pack/grnet/logos/grnet_logo_en.svg "GRNET Logo")
# GRNET eScience
eScience is a cloud-based integrated service platform for big data analytics offered by GRNET and the associated [~okeanos](http://okeanos.grnet.gr) IaaS.

## Orka package
Currently the codenamed *orka* (ver 0.1.1) CLI and Web interfaces enable ~okeanos users to create Hadoop 2.x \(YARN\) multi-node clusters (http://apache.hadoop.org) in order to run their big data algorithms. Researchers, university students and teachers can fully exploit the MapReduce (as well as others) programming paradigm without wasting time and resources in hardware maintenance, software setup, etc.

## Future
eScience software adopts the agile methodology. At the end of each development cycle (aka sprint) a new shippable software increment is delivered. Features to be included in future orka  versions include:

- submit jobs
- dashboard to manage your clusters
- provide your own configuration options
- Hadoop components (Pig, Hive, Spark, etc.)

## Architecture
On a high-level, Orka is being developed in a REST-API architectural fashion. Each client (CLI or Web) communicates with the eScience backend through REST calls. [schema](docs/orka_arch_diagram.png)

## Use it at your terminal
Detailed information about installing and running orka is located in orka/README.md.

## Homepage URL
Login to (http://83.212.114.81/) to create Hadoop clusters with your ~okeanos token. You need at least 2 VMs in an ~okeanos project to build the minimum YARN cluster.

[![Build Status](https://travis-ci.org/grnet/e-science.svg?branch=develop)](https://travis-ci.org/grnet/e-science)

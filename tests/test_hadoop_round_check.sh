#!/bin/bash
# Usage: round check for hadoop
# it checks different images
# and different jobs
# if the optional parameters are omitted the two defaults are used.
DEFAULTIMAGE='Hadoop-2.5.2'
DEFAULTJOB='pi'

IMAGE=$1 # Selected image. Defaults to DEFAULTIMAGE
JOB=$2 # Selected job. Defaults to DEFAULTJOB

if [ -z "$IMAGE" ]
then
	echo '======================================================='
	echo -e 'No image given, defaulting to '$DEFAULTIMAGE
	echo '======================================================='
	IMAGE=$DEFAULTIMAGE
fi
if [ -z "$JOB" ]
then
	echo '======================================================='
	echo -e 'No job given, defaulting to '$DEFAULTJOB
	echo '======================================================='
	JOB=$DEFAULTJOB
fi

#echo 'Create Cluster for testing'
#orka create HadoopRoundCheck 3 4 2048 20 4 2048 20 Standard escience.grnet.gr 2 128 --use_hadoop_image $IMAGE
#ret=$?
#echo "Cluster ID is $ret"

# missing step here... to retrieve cluster id and master ip

HOST=hduser@83.212.96.29

echo "Running pi"
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi 2 10000;
exit'


echo "Stopping hadoop"
orka hadoop stop $CLUSTERID

echo "Starting hadoop"
orka hadoop start $CLUSTERID

echo "Running pi..."

echo "Stopping hadoop"
orka hadoop stop $CLUSTERID

echo "Formatting hadoop"
orka hadoop format $CLUSTERID

echo "Starting hadoop"
orka hadoop start $CLUSTERID

echo "Running pi..."

echo "Destroying cluster"
orka destroy $CLUSTERID



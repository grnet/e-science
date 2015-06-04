#!/bin/bash

# 01. Create
# 02. Stop
# 03. Format
# 04. Start
# 05. runPI
# 06. wordcount
# 07. teragen
# 08. pithosFS registered
# 09. runPI pithosFS
# 10. wordcount pithosFS
# 11. teragen pithosFS
# 12. Destroy

# setUp
setUp(){
	local OKEANOS_TOKEN=$(cat .private/.config.txt | grep "token" |cut -d' ' -f3)
	echo -e '[global]\ndefault_cloud = ~okeanos\nignore_ssl = on\n[cloud "~okeanos"]\nurl = https://accounts.okeanos.grnet.gr/identity/v2.0\ntoken = '$OKEANOS_TOKEN'\n[orka]\nbase_url = http://83.212.115.45' > ~/.kamakirc
}
tearDown(){
	rm -f ~/.kamakirc
	rm -f _tmp.txt
	unset SSHPASS
}

setUp
# 01 Create
declare -a ARR_RESULT=($(orka create integration_test 2 2 2048 5 2 2048 5 standard escience.grnet.gr 2 128 --use_hadoop_image))
CLUSTER_ID=${ARR_RESULT[1]}
MASTER_IP=${ARR_RESULT[3]}
export SSHPASS=\'${ARR_RESULT[5]}\'
if [ -n "$CLUSTER_ID" ]; then
	printf "Create Cluster: OK\n"
	echo 0 >&1
else
	printf "Create Cluster: Fail\n"
	echo 1 >&1
fi

if [ -z "$CLUSTER_ID" ] 
 then
	echo "Couldn't create cluster"
	echo "Exiting"
	return 1 2>/dev/null || exit 1
fi

# 02 Stop
RESULT=$(orka hadoop stop $CLUSTER_ID)
if [ -n "$RESULT" ]; then
	printf "Stop Hadoop: OK\n"
	echo 0 >&1
else
	printf "Stop Hadoop: Fail\n"
	echo 1 >&1
fi

# 03 Format
RESULT=$(orka hadoop format $CLUSTER_ID)
if [ -n "$RESULT" ]; then
	printf "Format Hadoop: OK\n"
	echo 0 >&1
else
	printf "Format Hadoop: Fail\n"
	echo 1 >&1
fi

# 04 Start
RESULT=$(orka hadoop start $CLUSTER_ID)
if [ -n "$RESULT" ]; then
	printf "Start Hadoop: OK\n"
	echo 0 >&1
else
	printf "Start Hadoop: Fail\n"
	echo 1 >&1
fi

HOST=hduser@$MASTER_IP
ROOTHOST=root@$MASTER_IP
HADOOP_HOME=/usr/local/hadoop
# sshpass -e scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ~/.ssh/id_rsa.pub $ROOTHOST:/home/hduser/
# sshpass -e ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $ROOTHOST \
# 'cat /home/hduser/id_rsa.pub >> /home/hduser/.ssh/authorized_keys;
# rm -f /home/hduser/id_rsa.pub;
# exit'

# 05 runPI
sshpass -e ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.5.2.jar pi 2 10000' 2>&1 | tee _tmp.txt
RESULT=$(cat _tmp.txt | grep "Estimated value of Pi is" |cut -d' ' -f6)
rm -f _tmp.txt
if [ -n "$RESULT" ]; then
	printf "Hadoop runPI: OK\n"
	echo 0 >&1
else
	printf "Hadoop runPI: Fail\n"
	echo 1 >&1
fi

# 08 pithosFS registered
sshpass -e ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
'/usr/local/hadoop/bin/hdfs dfs -ls pithos://pithos/WordCount/' > _tmp.txt 2>&1
cat _tmp.txt
rm -f _tmp.txt

12
RESULT=$(orka destroy $CLUSTER_ID)
echo "12 Destroy:"$RESULT
if [ -n "$RESULT" ]; then
	printf "Destroy Cluster: OK\n"
	echo 0 >&1
else
	printf "Destroy Cluster: Fail\n"
	echo 1 >&1
fi

tearDown

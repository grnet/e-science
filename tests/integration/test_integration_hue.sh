#! /bin/bash
# file: tests/test_integration_hue.sh

# shunit2 compatible unittest file, requires shunit2 installed (apt-get install shunit2)

# Tests
# 01. Create Cluster
# 02. Stop Hadoop
# 03. Format Hadoop
# 04. (Re)Start Hadoop
# 05. runPI
# 06. wordcount
# 07. teragen
# 08. pithosFS is registered
# 09. wordcount pithosFS
# 10. teragen pithosFS
# 11. Destroy Cluster

# Load test helpers
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "${DIR}"/shunit2_helpers.sh

# Get this test suite's name
FULLNAME="$(basename "$0")"
THIS_TEST="${FULLNAME%.*}"

oneTimeSetUp(){
	# runs before whole test suite
	if [ -z "${STAGING_IP}" ]; then
		STAGING_IP=http://83.212.115.45
	fi
	local OKEANOS_TOKEN=$(cat .private/.config.txt | grep "token" |cut -d' ' -f3)
	echo -e '[global]\ndefault_cloud = ~okeanos\nignore_ssl = on\n[cloud "~okeanos"]\nurl = https://accounts.okeanos.grnet.gr/identity/v2.0\ntoken = '$OKEANOS_TOKEN'\n[orka]\nbase_url = '$STAGING_IP > ~/.kamakirc	
}

oneTimeTearDown(){
	# runs after whole test suite
	kamaki file delete out_teragen -r --yes
	rm -f _tmp.txt
	unset SSHPASS
	rm -f ~/.kamakirc
}

tearDown(){
	# runs after each separate test
	unset RESULT
	rm -f _tmp.txt
	endSkipping
}


# 01 
testClusterCreate(){
	# arrange
	# act
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		# orka create name_of_cluster size_of_cluster master_cpus master_ram master_disksize slave_cpus slave_ram slave_disksize disk_template project_name
		( $(orka create hue_integration_test 2 4 6144 10 4 6144 10 standard escience.grnet.gr --use_hadoop_image Hue-3.8.0 >_tmp.txt 2> /dev/null) ) & keepAlive $! " Working"
		declare -a ARR_RESULT=($(cat _tmp.txt))
		CLUSTER_ID=${ARR_RESULT[7]}
		MASTER_IP=${ARR_RESULT[9]}
		export SSHPASS=${ARR_RESULT[12]}
		if [ -n "$MASTER_IP" ]; then
			HOST=hduser@$MASTER_IP
			ROOTHOST=root@$MASTER_IP
			HADOOP_HOME=/usr/local/hadoop
			sshpass -e scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ~/.ssh/id_rsa.pub $ROOTHOST:/home/hduser/
			sshpass -e ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $ROOTHOST \
			'cat /home/hduser/id_rsa.pub >> /home/hduser/.ssh/authorized_keys;
			rm -f /home/hduser/id_rsa.pub;
			exit'
		fi
	else
		startSkipping
	fi
	# assert (assert* "fail message" <success_condition>)
	assertTrue 'Create Cluster Failed' '[ -n "$CLUSTER_ID" ]'
}

# 02
testHadoopStop(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		orka hadoop stop $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Stop Hadoop Failed' '[ "$RESULT" -eq 0 ]'
}

# 03
testHadoopFormat(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		orka hadoop format $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Format Hadoop Failed' '[ "$RESULT" -eq 0 ]'
}

# 04
testHadoopRestart(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		orka hadoop start $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Start Hadoop Failed' '[ "$RESULT" -eq 0 ]'
}

# 05 runPI
testHDFSrunPI(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi 2 10000' > _tmp.txt 2>&1
		RESULT=$(cat _tmp.txt | grep "Estimated value of Pi is" |cut -d' ' -f6)
		echo $RESULT
	else
		startSkipping
	fi
	assertTrue 'HDFS runPI Failed' '[ -n "$RESULT" ]'
}

# 06 wordcount
testHDFSwordcount(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hdfs dfs -put /usr/local/hadoop/LICENSE.txt LICENSE.txt' > _tmp.txt 2>&1
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount LICENSE.txt out_wordcount' > _tmp.txt 2>&1
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hdfs dfs -test -e out_wordcount/_SUCCESS' > _tmp.txt 2>&1
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'HDFS wordcount Failed' '[ "$RESULT" -eq 0 ]'
}

# 07 teragen
testHDFSteragen(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar teragen 2684354 out_teragen' > _tmp.txt 2>&1
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hdfs dfs -test -e out_teragen/_SUCCESS' > _tmp.txt 2>&1
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'HDFS teragen Failed' '[ "$RESULT" -eq 0 ]'
}

# 08 pithosFS registered
testRegisteredpithosFS(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hdfs dfs -ls pithos://pithos/WordCount/' > _tmp.txt 2>&1
		# RESULT=$(grep -i "found [0-9]* items" _tmp.txt)
		RESULT=$(grep -i -c "No FileSystem for scheme" _tmp.txt)
		RESULT=$(grep -i -c "Could not resolve hostname" _tmp.txt)
	else
		startSkipping
	fi
	assertTrue 'pithosFS registration Failed' '[ "$RESULT" -eq 0 ]'
}

# 09. wordcount pithosFS
testpithosFSwordcount(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
#		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
#		'/usr/local/hadoop/bin/hdfs dfs -put /usr/lib/hadoop/LICENSE.txt LICENSE.txt' > _tmp.txt 2>&1
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount pithos://pithos/WordCount/warpeace.txt out_pithos_wordcount' > _tmp.txt 2>&1
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hdfs dfs -test -e out_pithos_wordcount/_SUCCESS' > _tmp.txt 2>&1
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'pithosFS wordcount Failed' '[ "$RESULT" -eq 0 ]'
}

# 10. teragen pithosFS
testpithosFSteragen(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar teragen 1342177 pithos://pithos/out_teragen/' > _tmp.txt 2>&1
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hdfs dfs -test -e pithos://pithos/out_teragen/_SUCCESS' > _tmp.txt 2>&1
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'pithosFS teragen Failed' '[ "$RESULT" -eq 0 ]'
}

# 11 Destroy
testClusterDestroy(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ]; then
		orka destroy $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Destroy Cluster Failed' '[ "$RESULT" -eq 0 ]'
}

. shunit2

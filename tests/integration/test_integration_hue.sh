#! /bin/bash
# file: tests/test_integration_hue.sh

# shunit2 compatible unittest file, requires shunit2 installed (apt-get install shunit2)

# Tests
# 01. Create Cluster
# 02. Scale Cluster Up
# 03. Scale Cluster Down
# 04. Stop Hadoop
# 05. Format Hadoop
# 06. (Re)Start Hadoop
# 07. runPI
# 08. wordcount
# 09. teragen
# 10. pithosFS is registered
# 11. wordcount pithosFS
# 12. teragen pithosFS
# 13. Destroy Cluster

# Load test helpers
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "${DIR}"/shunit2_helpers.sh

# Get this test suite's name
FULLNAME="$(basename "$0")"
THIS_TEST="${FULLNAME%.*}"

oneTimeSetUp(){
	# runs before whole test suite
	checkPrereqs
}

oneTimeTearDown(){
	# runs after whole test suite
	kamaki file delete out_teragen -r --yes
	rm -f _tmp.txt
	unset SSHPASS
	[ "$KAMAKI_CLEANUP" = "true" ] && { rm -f ~/.kamakirc; }
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
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		# orka create name_of_cluster size_of_cluster master_cpus master_ram master_disksize slave_cpus slave_ram slave_disksize disk_template project_name
		local COMMAND='orka create hue_integration_test 3 4 6144 10 4 6144 10 standard '"${OKEANOS_PROJECT}"' --image Hue\-3\.11\.0 >_tmp.txt 2> /dev/null'
		( $(eval $COMMAND) ) & keepAlive $! " Working"
		declare -a ARR_RESULT=($(cat _tmp.txt))
		CLUSTER_ID=${ARR_RESULT[1]}
		MASTER_IP=${ARR_RESULT[3]}
		export SSHPASS=${ARR_RESULT[6]}
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
testClusterScaleUp(){
	# arrange
	# act
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		# orka node add cluster_id
		orka node add $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	# assert (assert* "fail message" <success_condition>)
	assertTrue 'Cluster Scale Up Failed' '[ "$RESULT" -eq 0 ]'	
}

# 03
testClusterScaleDown(){
	# arrange
	# act
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		# orka node remove cluster_id
		orka node remove $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	# assert (assert* "fail message" <success_condition>)
	assertTrue 'Cluster Scale Down Failed' '[ "$RESULT" -eq 0 ]'	
}

# 04
testHadoopStop(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		orka hadoop stop $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Stop Hadoop Failed' '[ "$RESULT" -eq 0 ]'
}

# 05
testHadoopFormat(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		orka hadoop format $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Format Hadoop Failed' '[ "$RESULT" -eq 0 ]'
}

# 06
testHadoopRestart(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		orka hadoop start $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Start Hadoop Failed' '[ "$RESULT" -eq 0 ]'
}

# 07 runPI
testHDFSrunPI(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $HOST \
		'/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi 2 10000' > _tmp.txt 2>&1
		RESULT=$(cat _tmp.txt | grep "Estimated value of Pi is" |cut -d' ' -f6)
		echo $RESULT
	else
		startSkipping
	fi
	assertTrue 'HDFS runPI Failed' '[ -n "$RESULT" ]'
}

# 08 wordcount
testHDFSwordcount(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
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

# 09 teragen
testHDFSteragen(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
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

# 10 pithosFS registered
testRegisteredpithosFS(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
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

# 11. wordcount pithosFS
testpithosFSwordcount(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
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

# 12. teragen pithosFS
testpithosFSteragen(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
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

# 13 Destroy
testClusterDestroy(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		orka destroy $CLUSTER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Destroy Cluster Failed' '[ "$RESULT" -eq 0 ]'
}

. shunit2

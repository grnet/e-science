#! /bin/bash
# file: tests/test_integration_drupal.sh

# shunit2 compatible unittest file, requires shunit2 installed (apt-get install shunit2)

# Tests
# 01. Create Vre Drupal server
# 02. Destroy Vre Drupal server

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
testDrupalCreate(){
	# arrange
	# act
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		# orka vre create name_of_server server_cpus server_ram server_disksize disk_template project_name
		local COMMAND='orka vre create drupal_integration_test 2 2048 20 Standard '"${OKEANOS_PROJECT}"' Deb8\-Drupal\-Final >_tmp.txt 2> /dev/null'
		( $(eval $COMMAND) ) & keepAlive $! " Working"
		declare -a ARR_RESULT=($(cat _tmp.txt))
		# server_id: xx\nserver_IP: x.x.x.x\nroot password: xxxx
		# (7 items, 0-based array, so relevant items at positions 1(server_id), 3(server_IP), 6(password))
		SERVER_ID=${ARR_RESULT[1]}
		SERVER_IP=${ARR_RESULT[3]}
		export SSHPASS=${ARR_RESULT[6]}
	else
		startSkipping
	fi
	# assert (assert* "fail message" <success_condition>)
	assertTrue 'Create Drupal Vre Server Failed' '[ -n "$SERVER_ID" ]'
}

# 02 Destroy
testDrupalDestroy(){
	if [ "$DO_INTEGRATION_TEST" = "$THIS_TEST" ] || [ "$FULL_TESTSUITE" = "true" ]; then
		orka vre destroy $SERVER_ID
		RESULT="$?"
	else
		startSkipping
	fi
	assertTrue 'Destroy Drupal Vre Server Failed' '[ "$RESULT" -eq 0 ]'
}

. shunit2

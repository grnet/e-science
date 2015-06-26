#! /bin/bash
# file: tests/helpers.sh

# Common functions used in integration test scripts

keepAlive()
{
    local PID=$1
    local MESSAGE=$2
    local DELAY=0.75
    local SPINNER='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $PID)" ]; do
        local temp=${SPINNER#?}
        printf "\r$2 [%c]  " "$SPINNER"
        local SPINNER=$temp${SPINNER%"$temp"}
        sleep $DELAY
        printf "\b\b\b\b\b\b"
    done
    printf "\r\033[2K"
}

checkHost(){
	[ "${TRAVIS}" ] && [ "${CONTINUOUS_INTEGRATION}" ] && { echo "INFO: Running on Travis CI." >&2; return 0; } || { echo "INFO: Running locally." >&2; return 1; }
}

checkPrereqs()
{
	checkHost
	[ -f .private/.config.txt ] || { echo "ERROR: .private/.config.txt required but not found. Aborting." >&2; exit 1; }
	command -v shunit2 >/dev/null 2>&1 || { echo "ERROR: shunit2 required but not installed. Aborting." >&2; exit 1; }
}
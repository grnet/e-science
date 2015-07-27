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
	command -v shunit2 >/dev/null 2>&1 || { echo "ERROR: shunit2 required but not installed. Aborting." >&2; exit 1; }
	checkHost
	local HOST="$?"
	if [ "$HOST" = 0 ]; then # on Travis CI
		[ -f .private/.config.txt ] || { echo "ERROR: .private/.config.txt required but not found. Aborting." >&2; exit 1; }
		if [ -z "${STAGING_IP}" ]; then
			STAGING_IP=http://83.212.115.45
		fi
		local OKEANOS_TOKEN=$(cat .private/.config.txt | grep "^token" |cut -d' ' -f3)
		echo -e '[global]\ndefault_cloud = ~okeanos\nignore_ssl = on\n[cloud "~okeanos"]\nurl = https://accounts.okeanos.grnet.gr/identity/v2.0\ntoken = '$OKEANOS_TOKEN'\n[orka]\nbase_url = '$STAGING_IP > ~/.kamakirc
		KAMAKI_CLEANUP=true
		FULL_TESTSUITE=false
	else
		[ -f ~/.kamakirc ] || { echo "ERROR: ~/.kamakirc required but not found. Aborting." >&2; exit 1; }
		local BASE_URL=$(cat ~/.kamakirc | grep "^base_url" |cut -d' ' -f3)
		[ -z "$BASE_URL" ] && { echo "WARNING: no base_url found in .kamakirc. base_url = http://x.x.x.x expected." >&2; }
		KAMAKI_CLEANUP=false
		FULL_TESTSUITE=true
	fi
	if [ -z "${OKEANOS_PROJECT}" ]; then
		OKEANOS_PROJECT=$(cat .private/.config.txt | grep "^name" |cut -d' ' -f3)
	fi
	if [ -z "${OKEANOS_PROJECT}" ]; then
		echo "WARNING: no okeanos project found in environment or .config.txt. Setting default." >&2;
		OKEANOS_PROJECT=escience.grnet.gr
	fi
	if [ -z "${VRE_IMAGE}" ]; then
		echo "WARNING: no vre image found in environment. Setting default." >&2;
		VRE_IMAGE=Deb8-Mediawiki-Docker
	fi
}
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
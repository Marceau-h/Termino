#!/usr/bin/env bash

set -efaoux pipefail

source .env_mazette > /dev/null 2>&1

set +a

if [ "$MAZETTE_OUTPUT" ]
then
    echo "MAZETTE_OUTPUT is set to '$MAZETTE_OUTPUT'"
else
    echo "MAZETTE_OUTPUT is not set, if you continue, no output will be saved"
    read -p "Continue? [ y / $(tput setaf 1)N$(tput sgr0) ] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo "Aborting"
        exit 1
    else
        echo "Caution, no output will be saved"
    fi
fi

cd "${FOLDER:=`pwd`/}"

# Ensure pwd has worked
if [ -z "${FOLDER%/*}" ]
then
    echo "The pwd command failed, leading to cd to $FOLDER"
    exit 1
fi

# git pull origin master --quiet || exit


if [ ! -d "venv" ]
then
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source "$FOLDER"/"venv/bin/activate"

# Ensure that we have everything we need
for package in `cat requirements.txt`
do
    if ! pip show $package > /dev/null
    then
        echo "Missing $package, trying to install it..."
        pip install $package
    fi
done

COMMAND="source $FOLDER/venv/bin/activate; python -m uvicorn api.api:app --host ${MAZETTE_HOST:-'0.0.0.0'} --port ${MAZETTE_PORT:-'8000'} --root-path ${ROOT_PATH:-'/'} --workers 8 --timeout-keep-alive 1000 --log-config log.conf"

printf "Starting mazette with command:\n"
echo "$COMMAND"

set +ue
IS_RUNNING=$(ps -aux | grep uvicorn | grep mazette_api)
if [ -z "$IS_RUNNING" ]
then
    set -ue
    echo "mazette service currently not running, starting gunicorn..."
    screen -S Mazette -dm bash -c "$COMMAND"
else
    set -ue
    echo "mazette already running, restarting..."
    screen -S Mazette -X quit
    screen -S Mazette -dm bash -c "$COMMAND"
fi

cd -

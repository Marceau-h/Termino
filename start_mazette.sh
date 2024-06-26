#!/usr/bin/env bash

set -efaoux pipefail

source .env_mazette > /dev/null 2>&1

set +a

cd "${FOLDER:=`pwd`/}"

# Ensure pwd has worked
if [ -z "${FOLDER%/*}" ]
then
    echo "The pwd command failed, leading to cd to $FOLDER"
    exit 1
fi

if [ ! -d "venv" ]
then
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source "$FOLDER"/"venv/bin/activate"

set +e
sed "s/\(.*\)\(--\|#\).*/\1/g" "requirements.txt" | grep -v '^ *#' | while IFS= read -r package
do
    if [[ "git" == *"$package"* ]]
    then
      package_name=$(echo "$package" | cut -d'@' -f1)
      package_url=$(echo "$package" | cut -d'@' -f2)
      if ! pip show "$package_name" > /dev/null
      then
          echo "Missing $package, trying to install it..."
          pip install git+"$package_url"@master
      fi
    else
      if ! pip show "$package" > /dev/null
      then
          echo "Missing $package, trying to install it..."
          pip install "$package"
      fi
    fi
done
set -e

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

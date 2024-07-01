#! /usr/bin/env sh

cd "$(dirname "$0")" || return

# set worker number
if [ -z "$WORKER_NUM" ]; then
  if [ -z "$MY_CPU_LIMIT" ]; then
    WORKER_NUM=4
  else
    WORKER_NUM=$((MY_CPU_LIMIT * 2))
  fi
fi

echo "WORKER_NUM=$WORKER_NUM"

# set port
if [ "$IS_HOST_NETWORK" = "1" ] && [ "$PORT0" ]; then
  PORT=$PORT0
else
  PORT=1234
fi

echo "PORT=$PORT"

# do not use reload under production mode
if [ "$IS_PROD_RUNTIME" ] || [ "$SERVICE_ENV" ]; then
  RELOAD_PARAM=""
else
  RELOAD_PARAM="--reload"
fi

echo "RELOAD_PARAM=$RELOAD_PARAM"

# initialize database
python initialize_database.py

# start app server with gunicorn
python -m gunicorn app:app --workers $WORKER_NUM --bind "[::]:$PORT" $RELOAD_PARAM --timeout 60 --graceful-timeout 10 &

PID=$!
trap 'echo "Stopping"; kill $PID' TERM INT
wait $PID

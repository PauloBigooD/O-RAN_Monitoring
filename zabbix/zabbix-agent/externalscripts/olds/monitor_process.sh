#!/bin/bash

PROCESS_NAME="$1"
METRIC="$2"

PID=$(pidof $PROCESS_NAME | awk '{print $1}')

# Ajusta o PID para o caso específico do processo "nr-softmodem"
if [ "$PROCESS_NAME" == "nr-softmodem" ] && [ ! -z "$PID" ]; then
  PID=$((PID - 1))
fi

if [ -z "$PID" ]; then
  echo "0"
  exit 1
fi

case $METRIC in
  cpu)
    ps -p $PID -o %cpu= | awk '{print $1}'
    ;;
  mem)
    ps -p $PID -o %mem= | awk '{print $1}'
    ;;
  *)
    echo "Invalid metric"
    exit 1
    ;;
esac


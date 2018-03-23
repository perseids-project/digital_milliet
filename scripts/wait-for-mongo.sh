#!/bin/sh

: ${MONGO_HOST:=mongo}
: ${MONGO_PORT:=27017}
: ${MONGO_RETRIES:=5}
: ${MONGO_WAIT:=1}

ii=1
while [ $ii -le $MONGO_RETRIES ]
do
  if nc -z $MONGO_HOST $MONGO_PORT
  then
    exec $*
  else
    echo "Waiting for Mongo at $MONGO_HOST:$MONGO_PORT attempt $ii/$MONGO_RETRIES..."
    sleep $MONGO_WAIT
  fi

  ii=$(($ii + 1))
done

exit 1

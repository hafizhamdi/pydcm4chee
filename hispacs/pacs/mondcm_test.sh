#!/bin/bash

inotifywait -e close_write -mrq --format %w%f /opt/dcm4chee/server/default/archive | while read INPUT
do
	python postdcm.py $INPUT
   # echo $INPUT >> /tmp/mywatcher.log
done

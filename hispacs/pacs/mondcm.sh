#!/bin/bash

inotifywait -e close_write -mrq --format %w%f /root/pacs/testdcm | while read INPUT
do
	python postdcm2.py $INPUT
   # echo $INPUT >> /tmp/mywatcher.log
done

#!/bin/bash

file=$1
port=$2
pairName=$3
awk -F, '{ print "HSET", "\"'$pairName'_"$1"_"$2"\"",0 ,"\"""\"",1,"\"""\"" }' "$file" | sed s/$/$'\r'/ | redis-cli -p $port --pipe #--pipe-timeout 0

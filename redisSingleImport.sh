#!/bin/bash

file=$1
awk -F, '{ print "HSET", "\"pair_"$1"_"$2"\"",0 ,"\""$3"\"",1,"\""$4"\"" }' "$file" | sed s/$/$'\r'/ | redis-cli -p $2 --pipe #--pipe-timeout 0

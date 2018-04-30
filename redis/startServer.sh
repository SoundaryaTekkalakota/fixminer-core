#!/bin/bash

#redis-server --dir $1 --dbfilename $2 --port $3
redis-server $1/redis.conf --dir $1 --dbfilename $2 --port $3 --daemonize yes

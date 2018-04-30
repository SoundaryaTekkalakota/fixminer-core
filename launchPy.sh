#!/bin/bash


source activate redisEnv

python -u $1 -i $2 -c $3 -p $4 -m $5 -t $6


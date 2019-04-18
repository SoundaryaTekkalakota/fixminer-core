#!/bin/bash


source activate redisEnv

PYTHONPATH=$1 python -u main.py -root $1 -job $2

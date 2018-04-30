#!/bin/bash

redis-cli -p $1 shutdown save

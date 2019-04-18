#!/bin/bash


for x in {1..10000} ; do
	java -jar CompareTrees.jar shape /Users/anil.koyuncu/projects/fixminer-all/enhancedASTDiff/python/data/redis/ ALLdumps-gumInput.rdb clusterl0-gumInputALL.rdb 1 10.91.100.184
done


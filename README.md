# FixMiner

* [I. Introduction of FixMiner](#user-content-i-introduction)
* [II. Environment setup](#user-content-ii-environment)
* [III. Replication Data](#user-content-iii-data)
* [IV. Step-by-Step execution](#user-content-iv-how-to-run)
* [V. Evaluation Result](#user-content-v-evaluation-result)
* [VI. Generated Patches](#user-content-vi-generated-patches)
* [VII. Structure of the project](#user-content-vii-structure-of-the-project)

## I. Introduction

Fixminer is an automated approach for semantic fix pattern mining based on an iterative, three-fold, clustering strategy.

## II. Environment setup
To run the tool please follow the steps below.

FixMiner uses anaconda to create virtual environments. And it requires jdk 1.8

Once anaconda is installed, please use the environment.yml to create the virtual environment, with following command:

    conda env create -f environment.yml


After creating the environment, activate it. It is containing necessary dependencies for redis, and python.

    source activate redisEnv

Download dataset from , to the root of the repository

    https://github.com/fixminer/dataset/raw/master/input/allDataset.7z

Unzip it,to the datasetPath path indicated in app.properties.

    7z x allDataset.7z
    
In order to launch FixMiner, execute the jar file:

    java -jar FixPatternMiner.jar app.properties
    
## III. Replication Data
Replication Data:
    singleBR.pickle 
    
    This pickle contains the list bug reports (i.e. bid) with the their corresponding fixes (i.e. commit) for each project in the dataset (i.e. project). 
    
   bugReports.7z.00X
   
    This is the dump of the bug reports archive extracted from each commit. These bug reports are not necessarily considered as BUG,CLOSED; this archive is the contins initial bug reports before identifying the fixes. 
    
   gumInput.7z.001
   
    This archive contains all the patches in our dataset, formatted in a way that can be processed by GumTree (i.e DiffEntries, prevFiles, revFiles)
    
   ALLbugReportsComplete.pickle
   
    The pickle object that represents the bug reports under the following columns 'bugReport', 'summary', 'description', 'created', 'updated', 'resolved', 'reporterDN', 'reporterEmail','hasAttachment', 'attachmentTime', 'hasPR', 'commentsCount'


## IV. Step-by-Step execution
App.properties:


FixMiner consists of several jobs that needs to run in order to extract fix pattern from the dataset.
It is necessary to run the FixMiner, following the order.
  1.ENHANCED AST DIFF calcuation

    By setting the jobType = ENHANCEDASTDIFF. This will create the ENHANCEDASTDIFF for the dataset regardless of the actionType.

  2.CACHE the enhanced AST Diff into memory cache

    By setting the jobType = CACHE
    
  3.SI search index construction.
  
    By setting the jobType = SI
    
  4.SIMI in order to compare the similarity between the trees.
  
    By setting the jobType = SIMI

  5.LEVEL1 mining

    By setting the jobType = LEVEL1

  6.LEVEL2 mining

    By setting the jobType = LEVEL2

  7.LEVEL3 mining

    By setting the jobType = LEVEL3
    
    
 A mining is iteration is executed for the actionType. In order to execute for all the actionTypes, the iteration should be repeated from 2-7 by changing the actionType.
    
  There are some additional parameters in the app.config. 
  
  actionType
    
    The admitted values are UPD,INS,DEL,MOV,MIX, which represents the ENHANCEDASTDIFF actions.
    UPD/INS/DEL/MOV considers tree where a single action operation is done in the action set
    MIX considers any action.
  
  parallelism
    
    The engine to use for parallelism. It is either FORKJOIN or AKKA. 
    FORKJOIN is recommended is the FixMiner is running on a single machine. 
    AKKA is suggested for distributed machines.
    
  numOfWorkers
  
    The number of workers that will be generated when AKKA is selected as the parallelism engine.
    
  cursor
  
    The maximum number of pairs in during the search index SI creation.
    
   eDiffTimeout
   
    The timeout value in seconds for the Enhanced Diff computation (ENHANCEDASTDIFF). 
    In case ENHANCEDASTDIFF step logs timeouts, this value can be increase. 
    
    
   The following parameters should be used when dealing with extremely large dataset. Otherwise, default values are suggested.
    
   isBigPair
    
    This flag when set to true, splits the pairs that into chunks as ..0.txt,1.txt etc. 
    
   chunk
   
    The extension of the pairs files. When isBigPair is set to false(which is default), it needs to be set as .csv 
    When isBigPair mode is activated then the SIMI step executed for each chunk by stepping the chunk as 0.txt, 1,txt) 
    
    
## V. Evaluation Result
## VI. Generated Patches
## VII. Structure of the project
    
    


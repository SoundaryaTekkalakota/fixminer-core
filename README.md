FixMiner uses anaconda to create virtual environments.

Once anaconda is installed, please use the environment.yml to create the virtual environment, with following command:

    conda env create -f environment.yml
    
In order to launch FixMiner, execute the jar file:
    java -jar FixPatternMiner.jar app.properties
    
    
App.properties:

It is necessary to run the FixMiner, following the order.

  1.ENHANCED AST DIFF calcuation

    By setting the jobType = ENHANCEDASTDIFF

  2.CACHE the enhanced AST Diff into memory cache

    By setting the jobType = CACHE

  3.LEVEL1 mining

    By setting the jobType = LEVEL1

  4.LEVEL2 mining

    By setting the jobType = LEVEL2

  5.LEVEL3 mining

    By setting the jobType = LEVEL3

    
    



import redis
import pandas as pd
import pickle as p

import os
from os.path import join
import re
import logging
import sys



def loadPairs(cluster, subCluster):
    redis_db = redis.StrictRedis(host="localhost", port=port, db=1)
    keys = redis_db.scan(0,match='match-'+cluster+'_'+ subCluster + "_*",count='100000')

    columns = ['pairs_key', 'pairs', 'path1', 'path2','match']
    matches = pd.DataFrame(columns=columns)
    ind = 0

    for key in keys[1]:
        result = []
        val = redis_db.get(key)
        val
        res = val.decode().split(',')
        result.append(res[0])
        result.append(res[1])
        result.append(','.join(res[2:]))
        result.insert(0,key.decode().split('_')[2:])
        result.insert(0,key.decode())
        matches.loc[ind] = result
        ind +=1
    return matches
    #p.dump(matches, open("dataset/matchesCluster.pickle", "wb"))



def getMapping(x):
    pair1,pair2 = x['pairs']
    p1 = x['path1']
    p2 = x['path2']
    pathMapping[pair1] = p1
    pathMapping[pair2] = p2



def getargs():
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', dest='inputPath', help='target porg folder')
    parser.add_argument('-c', dest='clusterPath', help='destination output folder')
    parser.add_argument('-p', dest='port', help='filename')
    parser.add_argument('-m', dest='matchesName', help='filename')
    parser.add_argument('-t', dest='threshold', help='threshold')
    parser.add_argument('-id', dest='indexFile', help='indexFile')

    args = parser.parse_args()


    return args

def setLogg():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(funcName)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

if __name__ == '__main__':
    setLogg()
    args = getargs()

    # bash /Users/anilkoyuncu/bugStudy/release/code/launchPy.sh /Users/anilkoyuncu/bugStudy/release/code/python/abstractPatchClusterLevel3.py /Users/anilkoyuncu/bugStudy/release/code/Defects4J/ /Users/anilkoyuncu/bugStudy/release/code/cluster-3lDefects4JALL 6399 /Users/anilkoyuncu/bugStudy/release/code/cluster-2lDefects4JALL 1 dummy
    if args.inputPath is None:
        inputPath = '/Users/anilkoyuncu/bugStudy/release/code/Defects4J/'
        # dumpFolder = '/Users/anilkoyuncu/bugStudy/dataset/GumTreeOutput13April'

        # inputPath = "/Users/anilkoyuncu/bugStudy/dataset/Defects4J/"

        # clusterPath = 'clusterDefect4J'
        cluster3Level = '/Users/anilkoyuncu/bugStudy/release/code/cluster-3lDefects4JALL'
        port = 6399
        # matchesName = 'matchesD4J'
        cluster2Level = '/Users/anilkoyuncu/bugStudy/release/code/cluster-2lDefects4JALL'
        threshold = '1'
    else:

        inputPath = args.inputPath
        cluster3Level = args.clusterPath
        port = args.port
        cluster2Level = args.matchesName

        threshold = args.threshold

    try:
        os.makedirs(cluster3Level, exist_ok=True)



        clusters = os.listdir(cluster2Level)
        for c in clusters:
            if c.startswith('.') or c.startswith('matches'):
                continue
            subClusters= os.listdir(join(cluster2Level,c))
            for sbC in subClusters:
                if sbC.startswith('.'):
                    continue

                matches =loadPairs(c,sbC)

                if(matches.__len__() == 0):
                    continue

                matches['tuples']=matches.pairs.apply(lambda x:tuple(x))

                col_combi = matches.tuples.values.tolist()
                import networkx

                g = networkx.Graph(col_combi)

                cluster = []
                for subgraph in networkx.connected_component_subgraphs(g):
                    logging.info(subgraph.nodes())
                    cluster.append(subgraph.nodes())


                selectedCluster = cluster
                pathMapping = dict()

                matches.apply(lambda x:getMapping(x),axis=1)

                selectedCluster = [i for i in cluster if len(i) >= int(threshold)]
                for idx,s in enumerate(selectedCluster):
                    # if(len (s)<int(threshold)):
                    #     continue
                    logging.info('exporting cluster %s', s)
                    for f in s:
                        dumpFile = pathMapping[f]
                        logging.info('exporting file %s', dumpFile)

                        fileName = dumpFile.split('/')[3]

                        from shutil import copyfile
                        src = cluster2Level + dumpFile

                        try:
                            os.makedirs(join(cluster3Level,c,sbC,str(idx)), exist_ok=True)
                            dst = join(cluster3Level,c,sbC,str(idx),fileName)
                            copyfile(src,dst)

                        except FileNotFoundError:
                            logging.error(src)
    except Exception as err:
        logging.error(err)



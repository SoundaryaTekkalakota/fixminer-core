from multiprocessing.pool import ThreadPool, Pool

import redis
import pandas as pd
import pickle as p

import os
from os.path import join,isfile
import re
import shutil
import logging
import sys



def localPairCore(aTuple):
    idx, key,redis_db = aTuple
    columns = ['pairs_key', 'pairs', 'path1', 'path2', 'chawatheSim', 'diceSim', 'jaccardSim', 'editDistance']
    matches = pd.DataFrame(columns=columns)


    val = redis_db.get(key)

    res = val.decode().split(',')
    res.insert(0, key.decode().split('_')[1:])
    res.insert(0, key.decode())
    matches.loc[idx] = res
    return matches

def loadPairMulti(clusterPath):

    if isfile(clusterPath +"/matches.pickle"):
        return pd.read_pickle(clusterPath +"/matches.pickle")
    else:
        redis_db = redis.StrictRedis(host="localhost", port=port, db=0)
        keys = redis_db.scan(0, match='match_*', count='3757068')

        tuples = []
        for idx,key in enumerate(keys[1]):
            t = idx,key,redis_db
            tuples.append(t)

        coreNumber = 160
        
        pool = ThreadPool(2 * coreNumber)

        data = pool.map(localPairCore, [link for link in tuples])

        pool.close()
        pool.join()

        dataL = pd.concat(data)
        # p.dump(dataL, open(clusterPath +"/matches.pickle", "wb"))
        return dataL



def getMapping(x):
    pair1,pair2 = x['pairs']
    p1 = x['path1']
    p2 = x['path2']
    pathMapping[pair1] = p1
    pathMapping[pair2] = p2



def setLogg():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(funcName)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
def getargs():
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', dest='inputPath', help='target porg folder')
    parser.add_argument('-c', dest='clusterPath', help='destination output folder')
    parser.add_argument('-p', dest='port', help='filename')
    parser.add_argument('-m', dest='matchesName', help='filename')
    parser.add_argument('-t', dest='threshold', help='threshold')

    args = parser.parse_args()


    return args

if __name__ == '__main__':
    setLogg()
    args = getargs()
    if args.inputPath is None:
        print('error')
    else:

        inputPath = args.inputPath
        clusterPath = args.clusterPath
        port = args.port
        matchesName = args.matchesName
        threshold = args.threshold

    os.makedirs(clusterPath, exist_ok=True)
    matches = loadPairMulti(clusterPath)

    matches['tuples']=matches.pairs.apply(lambda x:tuple(x))

    col_combi = matches.tuples.values.tolist()
    import networkx

    g = networkx.Graph(col_combi)

    cluster = []
    for subgraph in networkx.connected_component_subgraphs(g):
        print(subgraph.nodes())
        cluster.append(subgraph.nodes())

    cluster

    selectedCluster = [i for i in cluster if len(i)>int(threshold)]

    pathMapping = dict()

    matches.apply(lambda x:getMapping(x),axis=1)
    print(len(selectedCluster))
    pathMapping

    for idx,s in enumerate(selectedCluster):
        for f in s:
            dumpFile = pathMapping[f]
            project, type ,diffFile = dumpFile.split('/')


            try:

                project = project.replace('/','')
                fileName,position = diffFile.split('.txt_')
                fileName = fileName +".txt"

                # no external disk
                filePath = join(inputPath,project,"DiffEntries",fileName)

                with open(filePath, 'r', encoding='utf-8') as fi:
                    lines = fi.read()

                os.makedirs(join(clusterPath,str(idx)), exist_ok=True)
                with open(join(clusterPath,str(idx),fileName+'_'+position+'_'+project), 'w', encoding='utf-8') as writeFile:
                    writeFile.write(lines)

            except FileNotFoundError:
                print(dumpFile)






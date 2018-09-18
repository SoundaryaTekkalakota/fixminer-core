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
        print('Core number %s' % coreNumber)

        pool = ThreadPool(2 * coreNumber)

        data = pool.map(localPairCore, [link for link in tuples])

        pool.close()
        pool.join()

        dataL = pd.concat(data)
        p.dump(dataL, open(clusterPath +"/matches.pickle", "wb"))
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
    parser.add_argument('-id', dest='indexFile', help='indexFile')

    args = parser.parse_args()


    return args

if __name__ == '__main__':
    setLogg()
    args = getargs()
    if args.inputPath is None:
#bash /Users/anilkoyuncu/bugStudy/release/code/launchPy.sh /Users/anilkoyuncu/bugStudy/release/code/python/abstractPatch.py /Users/anilkoyuncu/bugStudy/release/code/Defects4J/ /Users/anilkoyuncu/bugStudy/release/code/clusterDefects4JALL 6399 matchesDefects4JALL 1
#bash /Users/anilkoyuncu/bugStudy/release/code/launchPy.sh /Users/anilkoyuncu/bugStudy/release/code/python/abstractPatch.py /Users/anilkoyuncu/bugStudy/release/code/Defects4J/ /Users/anilkoyuncu/bugStudy/release/code/clusterDefects4JINS 6399 matchesDefects4JINS 1 /Users/anilkoyuncu/bugStudy/release/code/pairsImportDefects4JINS/Defects4JINS.index
# #python -u $1 -i $2 -c $3 -p $4 -m $5 -t $6
        inputPath = '/Users/anilkoyuncu/bugStudy/release/code/Defects4J'
        # dumpFolder = '/Users/anilkoyuncu/bugStudy/dataset/GumTreeOutput13April'

        # inputPath = "/Users/anilkoyuncu/bugStudy/dataset/Defects4J/"

        # clusterPath = 'clusterDefect4J'
        clusterPath = '/Users/anilkoyuncu/bugStudy/release/code/clusterDefects4JINS'
        port = 6399
        # matchesName = 'matchesD4J'
        matchesName = 'matchesDefects4JALL'
        threshold = 1
        indexFile = '/Users/anilkoyuncu/bugStudy/release/code/pairsImportDefects4JINS/Defects4JINS.index'
    else:

        inputPath = args.inputPath
        clusterPath = args.clusterPath
        port = args.port
        matchesName = args.matchesName
        threshold = args.threshold
        indexFile = args.indexFile

    try:
        # logging.info('Parameters: \ninputPath %s \nclusterPath %s \nport %s \nmatchesName %s \nthreshold %s \n%indexFile',inputPath,clusterPath,str(port),matchesName,str(threshold),indexFile)
        os.makedirs(clusterPath, exist_ok=True)
        matches = loadPairMulti(clusterPath)

        project = inputPath.split('/')[-1]
        # indexName = clusterPath.split('/')[-1].replace('cluster','')

        matches['tuples']=matches.pairs.apply(lambda x:tuple(x))

        col_combi = matches.tuples.values.tolist()
        import networkx

        g = networkx.Graph(col_combi)

        cluster = []
        for subgraph in networkx.connected_component_subgraphs(g):
            logging.info(subgraph.nodes())
            cluster.append(subgraph.nodes())

        cluster

        selectedCluster = [i for i in cluster if len(i)>=int(threshold)]

        pathMapping = dict()

        df = pd.read_csv(indexFile, header=None,usecols=[0,1],index_col=[0])
        pathMapping = df.to_dict()

        # pathMapping[1][909]
        # matches.apply(lambda x:getMapping(x),axis=1)
        logging.info(len(selectedCluster))
        pathMapping = pathMapping[1]


        for idx,s in enumerate(selectedCluster):
            logging.info('exporting cluster %s',s)
            for f in s:

                dumpFile = pathMapping[int(f)]
                logging.info('exporting file %s', dumpFile)
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
                    logging.error(filePath)
    except Exception as ex:
        logging.error(ex)






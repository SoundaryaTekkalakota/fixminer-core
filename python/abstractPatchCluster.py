
import redis
import pandas as pd
import pickle as p

import os
from os.path import join
from os.path import isfile, join
import re
from multiprocessing.pool import ThreadPool, Pool
import logging
import sys




counter = 0
def localPairCore(aTuple):
    idx, key,redis_db,cluster = aTuple

    columns = ['pairs_key', 'pairs', 'path1', 'pj1', 'path2', 'pj2', 'chawatheSim', 'diceSim', 'jaccardSim',
               'editDistance']
    matches = pd.DataFrame(columns=columns)
    # global counter
    # print(counter)
    # counter = counter + 1

    val = redis_db.get(key)
    res = val.decode().split(',')
    res.insert(0, key.decode().split('_')[1:])
    res.insert(0, key.decode())
    matches.loc[idx] = res
    return matches



def loadPairMulti(clusterPath,cluster):
    print("cluster " + cluster)
    # if (isfile(clusterPath+"/matches.pickle" + cluster)):
    #     return pd.read_pickle(clusterPath+"/matches.pickle" + cluster)
    # connPool = redis.BlockingConnectionPool(host='localhost', port=port, db=1,max_connections=1000)
    redis_db = redis.StrictRedis(host="localhost", port=port, db=1)
    # redis_db = redis.StrictRedis(connection_pool=connPool)
    keys = redis_db.scan(0,match='match-'+cluster+'_*', count='2000000')

    tuples = []
    for idx,key in enumerate(keys[1]):
        t = idx,key,redis_db,cluster
        tuples.append(t)

    coreNumber = 100
    # print('Core number %s' % coreNumber)

    pool = ThreadPool(2 * coreNumber)

    data = pool.map(localPairCore, [link for link in tuples])

    pool.close()
    pool.join()
    try:
        dataL = pd.concat(data)
        # p.dump(dataL, open(clusterPath+"/matches.pickle" + cluster, "wb"))
    except ValueError:
        return None
    return dataL



def getMapping(x):
    pair1,pair2 = x['pairs']
    p1 = x['path1']
    p2 = x['path2']
    pj1 = x['pj1']
    pj2 = x['pj2']
    pathMapping[pair1] = pj1,p1.split('/')[2]
    pathMapping[pair2] = pj2,p2.split('/')[2]



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
    if args.inputPath is None:
        #bash /Users/anilkoyuncu/bugStudy/release/code/launchPy.sh /Users/anilkoyuncu/bugStudy/release/code/python/abstractPatch.py /Users/anilkoyuncu/bugStudy/release/code/Defects4J/ /Users/anilkoyuncu/bugStudy/release/code/clusterDefects4JALL 6399 matchesDefects4JALL 1
        # bash /Users/anilkoyuncu/bugStudy/release/code/launchPy.sh /Users/anilkoyuncu/bugStudy/release/code/python/abstractPatchCluster.py /Users/anilkoyuncu/bugStudy/release/code/allDataset/ /Users/anilkoyuncu/bugStudy/release/code/clusterallDatasetINS 6399 /Users/anilkoyuncu/bugStudy/release/code/cluster-2lallDatasetINS 1
        inputPath = '/Users/anilkoyuncu/bugStudy/release/code/allDataset/'
        # dumpFolder = '/Users/anilkoyuncu/bugStudy/dataset/GumTreeOutput13April'

        # inputPath = "/Users/anilkoyuncu/bugStudy/dataset/Defects4J/"

        # clusterPath = 'clusterDefect4J'
        clusterPath = '/Users/anilkoyuncu/bugStudy/release/code/clusterallDatasetINS'
        port = 6399
        # matchesName = 'matchesD4J'
        cluster2Level = '/Users/anilkoyuncu/bugStudy/release/code/cluster-2lallDatasetINS'
        threshold = 1
        indexFile = ''
    else:

        inputPath = args.inputPath
        clusterPath = args.clusterPath
        port = args.port
        cluster2Level = args.matchesName
        # matchesName = args.matchesName
        threshold = args.threshold
        indexFile = ''

    try:
        os.makedirs(cluster2Level, exist_ok=True)
        clusters = os.listdir(clusterPath)
        for c in clusters:
            if c.startswith('.'):
                continue

            matches =loadPairMulti(cluster2Level,c)

            if(matches is None):
                continue



            matches['tuples']=matches.pairs.apply(lambda x:tuple(x))

            col_combi = matches.tuples.values.tolist()
            import networkx

            g = networkx.Graph(col_combi)

            cluster = []
            for subgraph in networkx.connected_component_subgraphs(g):
                logging.info(subgraph.nodes())
                cluster.append(subgraph.nodes())


            pathMapping = dict()

            matches.apply(lambda x:getMapping(x),axis=1)

            pathMapping
            selectedCluster = [i for i in cluster if len(i) >= int(threshold)]
            for idx,s in enumerate(selectedCluster):
                # if (len(s) < int(threshold)):
                #     continue

                logging.info('exporting cluster %s', s)
                for f in s:
                    project, dumpFile = pathMapping[f]
                    logging.info('exporting file %s', dumpFile)
                    try:

                        fileName,position = dumpFile.split('.txt_')
                        fileName = fileName +".txt"

                        # filePath = join(clusterPath,c,dumpFile )
                        #
                        # with open(filePath, 'r', encoding='utf-8') as fi:
                        #     lines = fi.read()

                        filePath = join(inputPath, project, "DiffEntries", fileName)

                        with open(filePath, 'r', encoding='utf-8') as fi:
                            lines = fi.read()

                        os.makedirs(join(cluster2Level,c,str(idx)), exist_ok=True)
                        with open(join(cluster2Level,c,str(idx),dumpFile), 'w', encoding='utf-8') as writeFile:
                            writeFile.write(lines)



                    except FileNotFoundError:
                        logging.error(filePath)
    except Exception as err:
        logging.error(err)





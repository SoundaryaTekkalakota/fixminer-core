
import redis
import pandas as pd
import pickle as p

import os
from os.path import join
from os.path import isfile, join
import re
from multiprocessing.pool import ThreadPool, Pool





def localPairCore(aTuple):
    idx, key,redis_db,cluster = aTuple

    columns = ['pairs_key', 'pairs', 'path1', 'pj1', 'path2', 'pj2', 'chawatheSim', 'diceSim', 'jaccardSim',
               'editDistance']
    matches = pd.DataFrame(columns=columns)

    val = redis_db.get(key)
    res = val.decode().split(',')
    res.insert(0, key.decode().split('_')[1:])
    res.insert(0, key.decode())
    matches.loc[idx] = res
    return matches



def loadPairMulti(clusterPath,cluster):
    print("cluster " + cluster)
    if (isfile(clusterPath+"/matches.pickle" + cluster)):
        return pd.read_pickle(clusterPath+"/matches.pickle" + cluster)
    # connPool = redis.BlockingConnectionPool(host='localhost', port=port, db=1,max_connections=1000)
    redis_db = redis.StrictRedis(host="localhost", port=port, db=1)
    # redis_db = redis.StrictRedis(connection_pool=connPool)
    keys = redis_db.scan(0,match='match-'+cluster+'_*', count='2000000')

    tuples = []
    for idx,key in enumerate(keys[1]):
        t = idx,key,redis_db,cluster
        tuples.append(t)

    coreNumber = 100
    print('Core number %s' % coreNumber)

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

    args = parser.parse_args()


    return args

if __name__ == '__main__':
    # setLogg()
    args = getargs()
    if args.inputPath is None:
        print('error')
    else:

        inputPath = args.inputPath
        clusterPath = args.clusterPath
        port = args.port
        cluster2Level = args.matchesName
        # matchesName = args.matchesName
        threshold = args.threshold

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

            cluster.append(subgraph.nodes())


        pathMapping = dict()

        matches.apply(lambda x:getMapping(x),axis=1)

        pathMapping

        for idx,s in enumerate(cluster):
            if (len(s) < int(threshold)):
                continue
            for f in s:
                project, dumpFile = pathMapping[f]
                try:

                    fileName,position = dumpFile.split('.txt_')
                    fileName = fileName +".txt"

                    filePath = join(clusterPath,c,dumpFile )

                    with open(filePath, 'r', encoding='utf-8') as fi:
                        lines = fi.read()

                    os.makedirs(join(cluster2Level,c,str(idx)), exist_ok=True)
                    with open(join(cluster2Level,c,str(idx),dumpFile), 'w', encoding='utf-8') as writeFile:
                        writeFile.write(lines)

                except FileNotFoundError:
                    print(dumpFile)





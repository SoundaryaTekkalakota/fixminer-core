
import redis
import pandas as pd
import pickle as p

import os
from os.path import join
import re



def loadPairs(cluster, subCluster):
    print("cluster " + cluster + " subCluster " + subCluster)
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

    args = parser.parse_args()


    return args

if __name__ == '__main__':
    # setLogg()
    args = getargs()
    if args.inputPath is None:
        print('error')
    else:

        inputPath = args.inputPath
        cluster3Level = args.clusterPath
        port = args.port
        cluster2Level = args.matchesName

        threshold = args.threshold

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
                print(subgraph.nodes())
                cluster.append(subgraph.nodes())


            selectedCluster = cluster
            pathMapping = dict()

            matches.apply(lambda x:getMapping(x),axis=1)

            pathMapping
            if(c == 0 and sbC == 8):
                print()

            for idx,s in enumerate(selectedCluster):
                if(len (s)<int(threshold)):
                    continue
                for f in s:
                    dumpFile = pathMapping[f]

                    fileName = dumpFile.split('/')[3]

                    from shutil import copyfile
                    src = cluster2Level + dumpFile

                    try:
                        os.makedirs(join(cluster3Level,c,sbC,str(idx)), exist_ok=True)
                        dst = join(cluster3Level,c,sbC,str(idx),fileName)
                        copyfile(src,dst)

                    except FileNotFoundError:
                        print(src)




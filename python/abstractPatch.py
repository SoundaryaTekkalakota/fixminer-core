# from multiprocessing.pool import ThreadPool, Pool

import redis

from common.commons import *



def localPairCore(aTuple):
    redis_db = redis.StrictRedis(host="localhost", port=6380, db=1)
    idx, key = aTuple



    val = redis_db.get(key)

    res = val.decode().split(',')
    res.insert(0, key.decode().split('_')[1:])
    res.insert(0, key.decode())
    # matches.loc[idx] = res
    return res


def loadPairMulti(root,clusterPath,level):

    # root = 'BreakStatement'
    logging.info(root)
    port = 6380
    if isfile(clusterPath +"/"+root+".pickle"):
        return load_zipped_pickle(clusterPath +"/"+root+".pickle")
    else:
        # redis_db = redis.StrictRedis(host="localhost", port=port, db=1)  #L1
        redis_db = redis.StrictRedis(host="localhost", port=port, db=2)
        keys = redis_db.scan(0, match=root+'*', count='1000000')

        tuples = []
        for idx,key in enumerate(keys[1]):
            t = idx,key
            tuples.append(t)

        # coreNumber = 1600
        # print('Core number %s' % coreNumber)
        matches = pd.DataFrame(keys[1],columns=['pairs_key'])
        matches['pairs_key']=matches['pairs_key'].apply(lambda x:x.decode())
        matches['pairs']=matches['pairs_key'].apply(lambda x:x.split('_')[1:])
        matches['tuples'] = matches.pairs.apply(lambda x: tuple(x))
        matches['path1']=matches['pairs_key'].apply(lambda x:x.split('_')[1])
        matches['path2']=matches['pairs_key'].apply(lambda x:x.split('_')[2])
        matches['sizes']=matches['pairs_key'].apply(lambda x:x.split('_')[0].split('-')[1])
        if level == 'tokens':
            matches['actions']=matches['pairs_key'].apply(lambda x:x.split('_')[0].split('-')[2])


        # keys[1][0].decode()
        # columns = ['pairs_key', 'pairs', 'path1', 'path2', 'chawatheSim', 'diceSim', 'jaccardSim', 'editDistance']
        # matches = pd.DataFrame(columns=columns)
        # localPairCore(tuples[0])
        # d1 = parallelRunMerge(localPairCore,tuples)
        # logging.info('creating df')
        # matches = pd.DataFrame(d1,columns=columns)

        #
        # pool = ThreadPool(2 * coreNumber)

        # data = pool.map(localPairCore, [link for link in tuples])

        # pool.close()
        # pool.join()
        #
        # dataL = pd.concat(data)
        # dataL = parallelRunMerge(localPairCore,tuples)
        save_zipped_pickle(matches,clusterPath +"/"+root+".pickle")
        # p.dump(dataL, open(clusterPath +"/matches.pickle", "wb"))
        return matches



def getMapping(pathMapping,x):
    pair1,pair2 = x['pairs']
    p1 = x['path1']
    p2 = x['path2']
    pathMapping[pair1] = p1
    pathMapping[pair2] = p2




# if __name__ == '__main__':
#     setLogg()
#     args = getargs()
#     if args.inputPath is None:
# #bash /Users/anilkoyuncu/bugStudy/release/code/launchPy.sh /Users/anilkoyuncu/bugStudy/release/code/python/abstractPatch.py /Users/anilkoyuncu/bugStudy/release/code/Defects4J/ /Users/anilkoyuncu/bugStudy/release/code/clusterDefects4JALL 6399 matchesDefects4JALL 1
# #bash /Users/anilkoyuncu/bugStudy/release/code/launchPy.sh /Users/anilkoyuncu/bugStudy/release/code/python/abstractPatch.py /Users/anilkoyuncu/bugStudy/release/code/Defects4J/ /Users/anilkoyuncu/bugStudy/release/code/clusterDefects4JINS 6399 matchesDefects4JINS 1 /Users/anilkoyuncu/bugStudy/release/code/pairsImportDefects4JINS/Defects4JINS.index
# # #python -u $1 -i $2 -c $3 -p $4 -m $5 -t $6
#         inputPath = '/Users/anilkoyuncu/bugStudy/release/code/Defects4J'
#         # dumpFolder = '/Users/anilkoyuncu/bugStudy/dataset/GumTreeOutput13April'
#
#         # inputPath = "/Users/anilkoyuncu/bugStudy/dataset/Defects4J/"
#
#         # clusterPath = 'clusterDefect4J'
#         clusterPath = '/Users/anilkoyuncu/bugStudy/release/code/clusterDefects4JINS'
#         port = 6399
#         # matchesName = 'matchesD4J'
#         matchesName = 'matchesDefects4JALL'
#         threshold = 1
#         indexFile = '/Users/anilkoyuncu/bugStudy/release/code/pairsImportDefects4JINS/Defects4JINS.index'
#     else:

def cluster(inputPath,clusterPath,treePath,pairsPath, level):

            # inputPath = args.inputPath
            # clusterPath = args.clusterPath
            # port = args.port
            # matchesName = args.matchesName
            # threshold = args.threshold
            # indexFile = args.indexFile
        threshold = 2
        indexFile = ''
        try:
            # logging.info('Parameters: \ninputPath %s \nclusterPath %s \nport %s \nmatchesName %s \nthreshold %s \n%indexFile',inputPath,clusterPath,str(port),matchesName,str(threshold),indexFile)
            os.makedirs(clusterPath, exist_ok=True)
            roots = listdir(treePath)
            roots = [i for i in roots if not i.startswith('.')]

            # parallelRun(loadPairMulti,roots,clusterPath)
            for root in roots:
                matches = loadPairMulti(root,clusterPath,level)
                sizes = matches['sizes'].unique().tolist()
                for s in sizes:
                    match = matches[matches['sizes'] == s]

                    if level == 'tokens':
                        actions = match['actions'].unique().tolist()
                        for action in actions:
                            match = match[match['actions'] == action]
                            clusterCore(clusterPath, inputPath, level, match, pairsPath, root, s,action)
                    else:
                        clusterCore(clusterPath, inputPath, level, match, pairsPath, root, s,'')





        except Exception as ex:
            logging.error(ex)


def clusterCore(clusterPath, inputPath, level, match, pairsPath, root, s,action):
    col_combi = match.tuples.values.tolist()
    import networkx
    g = networkx.Graph(col_combi)
    cluster = []
    for subgraph in networkx.connected_component_subgraphs(g):
        logging.info(subgraph.nodes())
        cluster.append(subgraph.nodes())
    cluster
    pathMapping = dict()
    if level == 'tokens':
        indexFile = join(pairsPath, root, s,action+'.index')
    else:
        indexFile = join(pairsPath, root, s + '.index')
    df = pd.read_csv(indexFile, header=None, usecols=[0, 1], index_col=[0])
    pathMapping = df.to_dict()
    for idx, clus in enumerate(cluster):
        logging.info('exporting cluster %s', clus)
        for f in clus:
            dumpFile = pathMapping[1][int(f)]
            split = dumpFile.split('_')
            project = split[0]
            filename = "_".join(split[1:-1])
            filePath = join(inputPath, project, 'DiffEntries', filename)

            with open(filePath, 'r', encoding='utf-8') as fi:
                lines = fi.read()

            clusterSavePath = ''
            if level == 'shapes':
                clusterSavePath = join(clusterPath, root, str(idx))
            elif level == 'actions':
                clusterSavePath = join(clusterPath, root, s, str(idx))
            else:
                clusterSavePath = join(clusterPath, root, s,action, str(idx))

            os.makedirs(clusterSavePath, exist_ok=True)
            with open(join(clusterSavePath, dumpFile), 'w', encoding='utf-8') as writeFile:
                writeFile.write(lines)

# def restOfCluster(inputPath,matches):
#             project = inputPath.split('/')[-1]
#             # indexName = clusterPath.split('/')[-1].replace('cluster','')
#
#             matches['tuples']=matches.pairs.apply(lambda x:tuple(x))
#
#             col_combi = matches.tuples.values.tolist()
#             import networkx
#
#             g = networkx.Graph(col_combi)
#
#             cluster = []
#             for subgraph in networkx.connected_component_subgraphs(g):
#                 logging.info(subgraph.nodes())
#                 cluster.append(subgraph.nodes())
#
#             cluster
#
#             selectedCluster = [i for i in cluster if len(i)>=int(threshold)]
#
#             pathMapping = dict()
#
#             df = pd.read_csv(indexFile, header=None,usecols=[0,1],index_col=[0])
#             pathMapping = df.to_dict()
#
#             # pathMapping[1][909]
#             # matches.apply(lambda x:getMapping(x),axis=1)
#             logging.info(len(selectedCluster))
#             pathMapping = pathMapping[1]
#
#
#             for idx,s in enumerate(selectedCluster):
#                 logging.info('exporting cluster %s',s)
#                 for f in s:
#
#                     dumpFile = pathMapping[int(f)]
#                     logging.info('exporting file %s', dumpFile)
#                     project, type ,diffFile = dumpFile.split('/')
#
#
#                     try:
#
#                         project = project.replace('/','')
#                         fileName,position = diffFile.split('.txt_')
#                         fileName = fileName +".txt"
#
#                         # no external disk
#                         filePath = join(inputPath,project,"DiffEntries",fileName)
#
#                         with open(filePath, 'r', encoding='utf-8') as fi:
#                             lines = fi.read()
#
#                         os.makedirs(join(clusterPath,str(idx)), exist_ok=True)
#                         with open(join(clusterPath,str(idx),fileName+'_'+position+'_'+project), 'w', encoding='utf-8') as writeFile:
#                             writeFile.write(lines)
#
#                     except FileNotFoundError:
#                         logging.error(filePath)
#         except Exception as ex:
#             logging.error(ex)






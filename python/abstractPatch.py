
import redis

from common.commons import *

DATA_PATH = os.environ["DATA_PATH"]

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
        if level == 'actions':
            matches['actions']=matches['pairs_key'].apply(lambda x:x.split('_')[0].split('-')[2])


        save_zipped_pickle(matches,clusterPath +"/"+root+".pickle")
        return matches



def getMapping(pathMapping,x):
    pair1,pair2 = x['pairs']
    p1 = x['path1']
    p2 = x['path2']
    pathMapping[pair1] = p1
    pathMapping[pair2] = p2





def cluster(inputPath,clusterPath,treePath,pairsPath, level):

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

                    if level == 'actions':
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
    if level == 'actions':
        indexFile = join(pairsPath, root, s,action+'.index')
    elif level == 'shapes':
        indexFile = join(pairsPath, root, s + '.index')
    else:
        indexFile =''
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

            key = root + '/*/'+dumpFile
            cmd = 'java -jar ' + join(DATA_PATH,'Cluster2Pattern.jar') + " " + key

            o,e = shellGitCheckout(cmd)
            lines = o

            # with open(filePath, 'r', encoding='utf-8') as fi:
            #     lines = fi.read()

            clusterSavePath = ''
            if level == 'shapes':
                clusterSavePath = join(clusterPath, root,s, str(idx))
            elif level == 'actions':
                clusterSavePath = join(clusterPath, root, s,action, str(idx))
            else:
                clusterSavePath = join(clusterPath, root, s,action, str(idx))

            os.makedirs(clusterSavePath, exist_ok=True)
            with open(join(clusterSavePath, dumpFile), 'w', encoding='utf-8') as writeFile:
                writeFile.write(lines)









from common.commons import *
DATA_PATH = os.environ["DATA_PATH"]


def statsNormal(isFixminer=True):
    # tokens = join(DATA_PATH, 'tokens')
    # actions = join(DATA_PATH, 'actions')
    yList = []
    colNames = []
    for type in ['tokens', 'actions', 'shapes']:
        statsS,clusterDF = stats(type,isFixminer)

        matches = pd.DataFrame(statsS, columns=['cluster', 'memberCount'])
        matches.sort_values(by='memberCount', ascending=False, inplace=True)
        matches
        if isFixminer:
            matches.to_csv(join(DATA_PATH, "stats" + type + ".csv"), index=False)
        else:
            matches.to_csv(join(DATA_PATH, "statsDefects4J" + type + ".csv"), index=False)
        print(type, matches.memberCount.sum())
        yList.append(matches.memberCount.values.tolist())
        colNames.append(type)
    if isFixminer:
        from common.commons import plotBox
        plotBox(yList,colNames,'dist_clusterMembers.pdf',False,False)
    # for i in range(2, 21):
    #     print('%d %d %d' % (matches[matches.memberCount >= i].memberCount.sum(), len(matches[matches.memberCount >= i]),i))

    # save_zipped_pickle(join(DATA_PATH,'statsShapes'))

idx = 0
def stats(type,isFixminer=True):
    clustersDF = pd.DataFrame(columns=['cid', 'type', 'members'])


    shapesPath = join(DATA_PATH, type)
    shapes = listdir(shapesPath)
    shapes = [f for f in shapes if isdir(join(shapesPath, f))]
    shape = size = cluster = action = token = None

    def statsCore(cs):
        global idx
        if isFixminer:
            cs = [i for i in cs if not (
                    i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith(
                'closure-compiler') or i.startswith('joda-time') or i.startswith('mockito') or i.startswith(
                'jfreechart'))]
        else:
            cs = [i for i in cs if (
                    i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith(
                'closure-compiler') or i.startswith('joda-time') or i.startswith('mockito') or i.startswith(
                'jfreechart'))]
        if size == '1':
            return
        # print('Cluster %s : member size %s' % (shape+"-"+size +"-"+cluster, len(cs)))
        clusterSize = len(cs)
        if token is None:
            if action is None:
                # clusterSize = len(cs)
                # if clusterSize > 1:
                #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
                t = shape + "-" + size + "-" + cluster, clusterSize
                clustersDF.loc[idx] = [t, type, cs]
                idx = idx + 1
            else:
                # clusterSize = len(cs)
                # if clusterSize > 1:
                #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
                t = shape + "-" + size + "-" + cluster + "-" + action, clusterSize
                clustersDF.loc[idx] = [t, type, cs]
                idx = idx + 1
        else:
            # clusterSize = len(cs)
            # if clusterSize > 1:
            #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
            t = shape + "-" + size + "-" + cluster + "-" + action + "-" + token, clusterSize
            clustersDF.loc[idx] = [t, type, cs]
            idx = idx + 1
        # t = shape + "-" + size + "-" + cluster, len(cs)
        # if len(cs)>0:
        #     with open(join(shapesPath,t[0].replace('-','/'),cs[0]),'r') as pattern:
        #         line = pattern.read()
        #         if line.startswith('MOV') or line.startswith('DEL'):
        #             t = t[0],0
        if clusterSize > 1:
            statsS.append(t)

    statsS = []
    for shape in shapes:
        if shape.startswith('.'):
            continue
        sizes = listdir(join(shapesPath, shape))

        for size in sizes:
            if size.startswith('.'):
                continue
            clusters = listdir(join(shapesPath, shape, size))
            for cluster in clusters:
                if cluster.startswith('.'):
                    continue
                cs = listdir(join(shapesPath, shape, size, cluster))

                if shapesPath.endswith('shapes'):
                    cs = listdir(join(shapesPath, shape, size, cluster))
                    statsCore(cs)
                else:
                    # level3
                    for action in cs:
                        if action.startswith('.'):
                            continue
                        tokens = listdir(join(shapesPath, shape, size, cluster, action))
                        if shapesPath.endswith('actions'):
                            statsCore(tokens)
                        else:
                            for token in tokens:
                                if token.startswith('.'):
                                    continue
                                cs = listdir(join(shapesPath, shape, size, cluster, action, token))
                                statsCore(cs)
    return statsS,clustersDF


def defects4jStats():
    if (isfile(join(DATA_PATH, 'defects4j-mapping.pickle'))):
        matches = load_zipped_pickle(join(DATA_PATH, 'defects4j-mapping.pickle'))
    else:
        # defects4j mapping
        mapping = pd.read_csv('mapping.csv', header=None, index_col=None, sep=' ')
        mapping.rename(columns={0: 'repo', 1: "commit", 2: 'defects4jID'}, inplace=True)
        dbDir = join(DATA_PATH, 'redis')

        portInner = '6399'
        startDB(dbDir, portInner, "ALLdumps-gumInput.rdb")

        import redis

        redis_db = redis.StrictRedis(host="localhost", port=portInner, db=0)
        keys = redis_db.scan(0, match='*', count='1000000')

        matches = pd.DataFrame(keys[1], columns=['pairs_key'])

        # matches = load_zipped_pickle(join(DATA_PATH,'singleHunks'))
        matches['pairs_key'] = matches['pairs_key'].apply(lambda x: x.decode())
        matches['root'] = matches['pairs_key'].apply(lambda x: x.split('/')[0])
        matches['size'] = matches['pairs_key'].apply(lambda x: x.split('/')[1])
        matches['file'] = matches['pairs_key'].apply(lambda x: x.split('/')[2])
        matches['repo'] = matches['file'].apply(lambda x: x.split('_')[0])
        matches['commit'] = matches['file'].apply(lambda x: x.split('_')[2])
        matches['hunk'] = matches['pairs_key'].apply(lambda x: x.split('/')[2].split('_')[-1])
        matches['fileName'] = matches['pairs_key'].apply(lambda x: '_'.join(x.split('/')[2].split('_')[:-1]))

        # save_zipped_pickle(matches, join(DATA_PATH, 'matches.pickle'))
        matches = matches[matches.repo.apply(lambda i: (
                    i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith(
                'closure-compiler') or i.startswith('joda-time') or i.startswith('mockito') or i.startswith('jfreechart')))]
        # matches = matches[matches.repo.apply(lambda i:  (i.endswith('.git')))]
        matches['defects4jID'] = matches.apply(lambda x: mapping.query(
            "commit.str.startswith('{0}') and repo== '{1}'".format(x['commit'], x['repo'])).defects4jID.tolist(), axis=1)
        save_zipped_pickle(matches, join(DATA_PATH, 'defects4j-mapping.pickle'))

    if not isfile(join(DATA_PATH, 'defects4jcluster.pickle')):
        # matches = load_zipped_pickle(join(DATA_PATH,'defects4j-mapping.pickle'))
        clustersDF = pd.DataFrame(columns=['cid', 'type', 'members'])
        idx = 0


        def statsCore(cs, type):
            global idx

            cs = [i for i in cs if (
                    i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith(
                'closure-compiler') or i.startswith('joda-time') or i.startswith('mockito') or i.startswith('jfreechart'))]
            # print('Cluster %s : member size %s' % (shape+"-"+size +"-"+cluster, len(cs)))
            if len(cs) > 0:
                if token is None:
                    if action is None:
                        t = shape + "-" + size + "-" + cluster

                        clustersDF.loc[idx] = [t, type, cs]
                        idx = idx + 1
                    else:
                        t = shape + "-" + size + "-" + cluster + "-" + action  # , len(cs)
                        clustersDF.loc[idx] = [t, type, cs]
                        idx = idx + 1
                else:
                    # clusterSize = len(cs)
                    # if clusterSize > 0:
                    #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
                    t = shape + "-" + size + "-" + cluster + "-" + action + "-" + token  # , clusterSize
                    clustersDF.loc[idx] = [t, type, cs]
                    idx = idx + 1


        for type in ['tokens', 'actions', 'shapes']:
            shapesPath = join(DATA_PATH, type)
            shapes = listdir(shapesPath)
            shapes = [f for f in shapes if isdir(join(shapesPath, f))]
            shape = size = cluster = action = token = None

            for shape in shapes:
                if shape.startswith('.'):
                    continue
                sizes = listdir(join(shapesPath, shape))

                for size in sizes:
                    if size.startswith('.'):
                        continue
                    clusters = listdir(join(shapesPath, shape, size))
                    for cluster in clusters:
                        if cluster.startswith('.'):
                            continue
                        cs = listdir(join(shapesPath, shape, size, cluster))

                        if shapesPath.endswith('shapes'):
                            cs = listdir(join(shapesPath, shape, size, cluster))
                            statsCore(cs, 'shapes')
                        else:
                            # level3
                            for action in cs:
                                if action.startswith('.'):
                                    continue
                                tokens = listdir(join(shapesPath, shape, size, cluster, action))
                                if shapesPath.endswith('actions'):
                                    statsCore(tokens, 'actions')
                                else:
                                    for token in tokens:
                                        if token.startswith('.'):
                                            continue
                                        cs = listdir(join(shapesPath, shape, size, cluster, action, token))
                                        statsCore(cs, 'tokens')

        # clustersDF
        # number of instances
        # clustersDF[clustersDF.type == 'tokens'].members.str.len().sum()
        # cluster len
        # len(clustersDF[clustersDF.type == 'shapes'])
        matches['defects4jID'] = matches['defects4jID'].apply(lambda x: x[0])


        def getDefects4JID(x):
            # filenames = list(set([re.split('.txt_[0-9]+', i)[0] for i in x]))
            # bids2Compare = [matches[matches.file.str.startswith(fn)].defects4jID.unique()[0] for fn in filenames]
            keys = []
            for fn in x:
                selected = matches[matches.file == fn]
                if len(selected) != 1:
                    print('erro')
                else:
                    key = selected.iloc[0]['repo'] + '-' + str(selected.iloc[0]['defects4jID'])
                    keys.append(key)

            return list(set(keys))


        clustersDF['defects4j'] = clustersDF.members.apply(lambda x: getDefects4JID(x))
        p
        save_zipped_pickle(clustersDF, join(DATA_PATH, 'defects4jcluster.pickle'))
    else:
        clustersDF = load_zipped_pickle(join(DATA_PATH, 'defects4jcluster.pickle'))
    clustersDF
    clustersDF['ms'] = clustersDF.members.str.len()

    for t in ['shapes', 'actions', 'tokens']:
        ds = clustersDF[clustersDF.type == t]
        ds.sort_values(by='ms', ascending=False, inplace=True)
        ds = ds[ds.ms > 1]

        ds[['cid', 'ms', 'defects4j']].to_csv(join(DATA_PATH, 'dissectionDefects4j' + t + '.csv'), index=None, header=None)

        print(t, ds.ms.sum(), len(ds))
        hunks = list(itertools.chain.from_iterable(ds.members.values.tolist()))
        bugs = set(list(itertools.chain.from_iterable(ds.defects4j.values.tolist())))
        print(len(hunks), len(bugs))

        keys = [tuple(i.rsplit('-', 1)) for i in bugs]

        test = pd.read_json(join(DATA_PATH, 'defects4j-bugs.json'))
        test['newKey'] = test.apply(lambda x: tuple([x['program'], str(x['bugId'])]), axis=1)
        selectBugs = test[test.newKey.isin(keys)]
        patterns = selectBugs[['program', 'bugId', 'repairPatterns']]
        patterns['oId'] = patterns.apply(lambda x: x['program'] + '-' + str(x['bugId']), axis=1)
        patterns['oId'].apply(lambda x: ds[ds.defects4j.apply(lambda y: x in y)].cid.values.tolist())
        patterns['myPatterns'] = patterns['oId'].apply(
            lambda x: ds[ds.defects4j.apply(lambda y: x in y)].cid.values.tolist())
        classification = pd.read_json(join(DATA_PATH, 'classification.json'))

        classKeys = classification[~classification['Repair Patterns'].isna()]['Repair Patterns'].values.tolist()
        classKeys = list(itertools.chain.from_iterable([list(i.keys()) for i in classKeys]))
        classKeys.remove('notClassified')
        patterns.repairPatterns = patterns.repairPatterns.apply(lambda x: [i for i in x if i in classKeys])
        dissectionPattern = set(itertools.chain.from_iterable(patterns['repairPatterns'].values.tolist()))


        def cmp(a, b):
            if a > b:
                return 'Dissection'
            elif a == b:
                return 'Equal'
            else:
                return 'Fixminer'


        patterns['cmp'] = patterns.apply(lambda x: cmp(len(x['repairPatterns']), len(x['myPatterns'])), axis=1)
        patterns.to_csv(join(DATA_PATH, 'dissectionPatterns' + t + '.csv'), index=None, header=None)
        print(patterns['cmp'].value_counts())
        myPatterns = set(itertools.chain.from_iterable(patterns['myPatterns'].values.tolist()))
        print(len(dissectionPattern), len(myPatterns))
        # classification = pd.read_json(join(DATA_PATH, 'classification.json'))
from common.commons import *
DATA_PATH = os.environ["DATA_PATH"]


def statsNormal(isFixminer=True):
    # tokens = join(DATA_PATH, 'tokens')
    # actions = join(DATA_PATH, 'actions')
    df = load_zipped_pickle('datasetGroupByHunk.pickle')
    yList = []
    colNames = []

    def haveAll(x):
        check = dict()
        if len(x)<2:
            return False
        for hunk in x:
            filename, hunkNo = hunk.rsplit('_',1)
            if filename in check:
                check[filename].append(hunkNo)
            else:
                check[filename] = [hunkNo]

        tv = []
        for k,v in check.items():
            selected = df[df.fileName == k]
            if tuple(selected.iloc[0].hunk) == tuple(v):
                tv.append(True)
            else:
                tv.append(False)
        result = np.all(tv)
        return result

    def combinationOfPatterns(x):
        check = dict()
        if len(x)<2:
            return False
        for hunk in x:
            filename, hunkNo = hunk.rsplit('_',1)
            if filename in check:
                check[filename].append(hunkNo)
            else:
                check[filename] = [hunkNo]

        tv = []

        res = check.copy()
        for k,v in check.items():
            # if len(v) == 1:
            #     res.pop(k,None)
            selected = df[df.fileName == k]
            if set(selected.iloc[0].hunk) != set(v):
                res.pop(k, None)
        # result = np.all(tv)
        indices = [i for i, val in enumerate(tv) if val == True]
        return res
    allHunks = []
    def test(x):
        try:
            fileList = []
            for i in x:

                fileName = i.rsplit('_', 1)[0]

                if fileName in byCombi.keys():
                    fileList.append(i)
            if len(fileList) > 0:

                if (set(fileList).issubset(set(x))):
                    # logging.info("In the same pattern")
                    allHunks.extend(fileList)
                    return True
                else:
                  logging.info("Mix")
            return False
        except Exception as e:
            logging.error(e)


    for type in ['tokens', 'actions', 'shapes']:
        statsS,clusterDF = stats(type,isFixminer)
        if isFixminer:
            clusterDF = clusterDF[clusterDF.members.str.len() > 1]

            clusterDF['vertical'] = clusterDF.members.apply(lambda x:len(set([i.rsplit('_',1)[0] for i in x])) == 1)
            clusterDF['v-h'] = clusterDF.members.apply(lambda x: len(set([i.rsplit('_', 1)[0] for i in x])))
            clusterDF['ms'] = clusterDF.members.apply(lambda x: len(x))
            clusterDF['horizontal'] = clusterDF.apply(lambda x: x['ms'] == x['v-h'] and x['v-h'] > 1, axis=1)



            logging.info('Spread horizontal %d vertical %d',len(clusterDF[clusterDF['horizontal'] == True]),  len(clusterDF[clusterDF['vertical'] == True]))
            logging.info('Spread patch horizontal %d vertical %d',clusterDF[clusterDF['horizontal'] == True]['v-h'].sum(),  clusterDF[clusterDF['vertical'] == True]['v-h'].sum())
            logging.info('Spread hunks horizontal %d vertical %d',clusterDF[clusterDF['horizontal'] == True]['ms'].sum(),  clusterDF[clusterDF['vertical'] == True]['ms'].sum())

        singlePatternAll= clusterDF[clusterDF.members.apply(lambda x:haveAll(x))]
        singlePatterns = list(set(singlePatternAll.cid.values.tolist()))

        # if type == 'actions':
        #     print('\n'.join(singlePatterns))
        hunks = set(itertools.chain.from_iterable(singlePatternAll.members.values.tolist()))
        logging.info("Match every member Fix\n %s # bugs: %d , # hunks %d ,#patterns %d", type,len(set([re.split('.txt_[0-9]+', i)[0] for i in hunks])),
                     len(hunks),
                     len(singlePatternAll))
        # nonEmpty = clusterDF[clusterDF.members.str.len() > 1]
        allhunks =set(itertools.chain.from_iterable(clusterDF.members.values.tolist()))
        byCombi = combinationOfPatterns(allhunks)


        multiple =clusterDF[clusterDF.members.apply(lambda x:test(x))]
        # print(len(multiple))
        # print(set(multiple.cid.values.tolist()).difference(singlePatterns))

        allHunks
        logging.info("%d patterns can match %d bugs, %d hunks",len(multiple),len(set([re.split('.txt_[0-9]+', i)[0] for i in allHunks])), len(allHunks))
        matches = pd.DataFrame(statsS, columns=['cluster', 'memberCount'])
        matches.sort_values(by='memberCount', ascending=False, inplace=True)
        matches
        if isFixminer:
            matches.to_csv(join(DATA_PATH, "stats" + type + ".csv"), index=False)
            if type == 'actions':
                clusterDF['ms'] = clusterDF.members.str.len()
                clusterDF.sort_values(by='ms', ascending=False, inplace=True)
                top50 = clusterDF.head(50)
                top50['member'] = top50.members.apply(lambda x: x[0])
                top50['cid'] = top50.cid.apply(lambda x: x[0])
                top50['path'] = top50.apply(lambda x:x['cid'].replace('-','/')+'/'+x['member'],axis=1)
                def readFile(x):
                    with open(join(DATA_PATH,'actions',x), 'r', encoding='utf-8') as writeFile:
                        lines = writeFile.read()
                        return lines
                        # if lines.startswith('UPD'):
                        #     return lines
                        # else:
                        #     return ''
                    # return lines

                top50['pattern'] = top50.path.apply(lambda x:readFile(x))
                top50[['cid','pattern']].to_csv('actionsPattern2verify.csv',index=False,header=None)








        else:
            matches.to_csv(join(DATA_PATH, "statsDefects4J" + type + ".csv"), index=False)
        print(type, matches.memberCount.sum())
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
        if isFixminer:
            if clusterSize > 1:
                statsS.append(t)
        else:
            if clusterSize > 0:
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


def defects4jStats(isFixminer=False):
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
        # clustersDF = pd.DataFrame(columns=['cid', 'type', 'members'])
        # idx = 0
        clustersL = []
        for type in ['tokens', 'actions', 'shapes']:
            statsS, clustert = stats(type, isFixminer)
            clustert =clustert[clustert.members.apply(lambda x:len(x)>0)]
            clustersL.append(clustert)
        clustersDF = pd.concat(clustersL)

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
        # ds = ds[ds.ms > 1]

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
        patterns['actions'] = selectBugs['repairActions']
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

        dissection = ds
        dissection['cid'] = dissection.cid.apply(lambda x: x[0])
        dissection = dissection[['cid', 'defects4j']]
        dissection['repairPatterns'] = dissection.defects4j.apply(lambda x:set([tuple(patterns[patterns.oId == i].iloc[0].repairPatterns) for i in x]))
        notSingle = dissection[dissection.defects4j.str.len() != 1]

        notSingle['repairPatterns'] = notSingle.repairPatterns.apply(lambda x:set.intersection(*[set(i) for i in x]))
        notSingle = notSingle[notSingle.repairPatterns != set()]
        notSingle.repairPatterns =notSingle.repairPatterns.apply(lambda i: {tuple(i)})
        # myDataset = notSingle[notSingle.repairPatterns.str.len() == 1]
        myDataset = dissection[dissection.defects4j.str.len() == 1]
        myPatterns = pd.concat([notSingle, myDataset])

        print(len(set.union(*myPatterns.repairPatterns.values.tolist())))

        myPatterns.repairPatterns = myPatterns.repairPatterns.apply(lambda x: list(x.pop()))
        allPAtterns =  myPatterns.repairPatterns.values.tolist()
        [i.sort() for i in allPAtterns]

        counts = Counter([tuple(i) for i in allPAtterns]).items()
        granularity = {k: v for k, v in counts if v > 1 and k != tuple()}
        print('consisteny %' ,sum([v for k, v in counts if k != tuple()]))
        print('Granularity %', len(granularity))



        myPatterns.to_csv(join(DATA_PATH, 'dissectionMyPatterns' + t + '.csv'), index=None, header=None)

        # dissectionPatterns = [list(i) for i in set.union(*myPatterns.repairPatterns.values.tolist())]
        # [i.sort() for i in dissectionPatterns]
        # print(len(set.union(*[{tuple(i)} for i in dissectionPatterns])))
        # logging.info('%s Unique label %d',t, len(set(list(itertools.chain.from_iterable(myDataset.repairPatterns.values.tolist())))))
        # def cmp(a, b):
        #     if a > b:
        #         return 'Dissection'
        #     elif a == b:
        #         return 'Equal'
        #     else:
        #         return 'Fixminer'
        #
        #
        # patterns['cmp'] = patterns.apply(lambda x: cmp(len(x['repairPatterns']), len(x['myPatterns'])), axis=1)
        # patterns.to_csv(join(DATA_PATH, 'dissectionPatterns' + t + '.csv'), index=None, header=None)
        # print('Pattern')
        # print(patterns['cmp'].value_counts())
        # patterns['cmpActions'] = patterns.apply(lambda x: cmp(len(x['actions']), len(x['myPatterns'])), axis=1)
        # print('Action')
        # print(patterns['cmpActions'].value_counts())
        # myPatterns = set(itertools.chain.from_iterable(patterns['myPatterns'].values.tolist()))
        # print(len(dissectionPattern), len(myPatterns))
        # # classification = pd.read_json(join(DATA_PATH, 'classification.json'))
        #
        # patterns.repairPatterns = patterns.repairPatterns.apply(lambda x: tuple(x))
        # logging.info('%s # Dissection Patterns %d, Unique %d, Empty %d',t, len(patterns['repairPatterns'].values.tolist()) -patterns['repairPatterns'].values.tolist().count(()),
        # len(set(patterns['repairPatterns'].values.tolist())),patterns['repairPatterns'].values.tolist().count(()))
        #
        # myPatterns = patterns.myPatterns.str.len().values.tolist()
        # repairPatterns = patterns.repairPatterns.str.len().values.tolist()
        # actions = patterns.actions.str.len().values.tolist()
        #
        #
        #
        #
        # plotScatter(myPatterns,repairPatterns,"# FixMiner Patterns",'# Dissection Patterns',11,t+'Fixminer-Patterns')
        # plotScatter(myPatterns,actions,"# FixMiner Patterns",'# Dissection Patterns',21,t+'Fixminer-Actions')

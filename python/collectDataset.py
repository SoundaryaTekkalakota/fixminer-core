from common.commons import *





if __name__ == '__main__':


    try:
        args = getRun()
        setLogg()


        setEnv(args)

        # job = args.job
        job = 'stats'
        ROOT_DIR = os.environ["ROOT_DIR"]
        REPO_PATH = os.environ["REPO_PATH"]
        CODE_PATH = os.environ["CODE_PATH"]
        DATA_PATH = os.environ["DATA_PATH"]
        COMMIT_DFS = os.environ["COMMIT_DFS"]
        BUG_POINT = os.environ["BUG_POINT"]
        COMMIT_FOLDER = os.environ["COMMIT_FOLDER"]
        FEATURE_DIR = os.environ["FEATURE_DIR"]
        DATASET_DIR = os.environ["DATASET_DIR"]

        pd.options.mode.chained_assignment = None


        #dataset stats
        #matches = load_zipped_pickle( join(DATA_PATH, 'studyDataset.pickle'))
        #matches = matches[matches.repo.apply(lambda i: not (i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith('closure-compiler.git') or i.startswith('joda-time.git') or i.startswith('mockito.git')))]
        #ds =matches.groupby('repo', as_index=False).agg({'bid': "nunique"})
        #ds['repo'] = ds['repo'].apply(lambda x:subjects.query("Repo == '{0}'".format(x)).iloc[0].Group.upper() +'-'+subjects.query("Repo == '{0}'".format(x)).iloc[0].Subject)
        #ds.sort_values(by='repo').to_latex('dataset.tex')




        if job == 'clone':
            from commitCollector import *

            caseClone(args.subject)
        elif job == 'collect':
            from commitCollector import *

            caseCollect(args.subject)
        elif job == 'fix':
            from filterBugFixingCommits import caseFix

            caseFix(args.subject)

        # elif job =='getSingleFix':
        #     for i in listdir(COMMIT_DFS):
        #         commits = load_zipped_pickle(join(COMMIT_DFS,i))
        #
        #         singleFix = commits.fix.value_counts().loc[lambda x: x == 1].reset_index(name='count')['index']
        #
        #         singleCommits = commits[commits.fix.isin(singleFix)]
        #         singleCommits['fix'] = singleCommits.fix.apply(lambda x: x.strip().upper())
        #         save_zipped_pickle(singleCommits,join(COMMIT_DFS,i))

        elif job =='brDownload':
            from bugReportDownloader import caseBRDownload
            caseBRDownload(args.subject)
        elif job =='brParser':
            from bugReportParser import step1
            step1(args.subject)

        elif job == 'datasetDefects4J':
            from defects4JDataset import core
            core()

        elif job =='dataset':

            if not isfile(join(DATA_PATH,'singleBR.pickle')):

                brs = load_zipped_pickle(join(DATA_PATH, args.subject + "bugReportsComplete.pickle"))

                subjects = pd.read_csv(join(DATA_PATH, 'subjects.csv'))
                # subjects['Group'] = subjects.Group.apply(
                #     lambda x: x.replace('Commons', 'Apache').replace('Wildfly', 'Jboss').upper())

                brs['project'] = brs.bugReport.apply(lambda x: x.split('-')[0])
                # brs['project'] = brs.project.apply(
                #     lambda x: subjects.query("Subject == '{0}'".format(x)).Group.tolist()[0] + '-' + x)

                def getCommit(x):
                    subjects = pd.read_csv(join(DATA_PATH, 'subjects.csv'))
                    repo = subjects.query("Subject == '{0}'".format(x['project'])).Repo.tolist()[0]
                    commits = load_zipped_pickle(join(DATA_PATH, COMMIT_DFS, repo+'.pickle'))
                    correspondingCommit=commits.query("fix =='{0}'".format(x['bid'])).commit.tolist()
                    if len(correspondingCommit) == 1:
                        return correspondingCommit[0]
                    else:
                        return None
                        print('error')

                brs['commit'] = brs.apply(lambda x:getCommit(x),axis=1)
                singleBR = brs[~brs.commit.isna()]
                singleBR = singleBR[['bid', 'commit', 'project']]
                save_zipped_pickle(singleBR,join(DATA_PATH,'singleBR.pickle'))
            else:
                commits = load_zipped_pickle(join(DATA_PATH,'singleBR.pickle'))
                subjects = pd.read_csv(join(DATA_PATH, 'subjects.csv'))

                commits['repo'] = commits.project.apply(lambda x:subjects.query("Subject == '{0}'".format(x)).Repo.tolist()[0])

                workList = commits[['commit','repo']].values.tolist()
                from dataset import prepareFiles
                # workList = ['9a45e0a9ded094d18bdcbbcaf4cf3944e7faf6d9', 'hbase']
                # for wl in workList:
                #     prepareFiles(wl)
                parallelRun(prepareFiles,workList)

        elif job =='calculatePairs':
            from pairs import shapePairs
            shapePairs()
        elif job == 'importShapesPairs':
            from pairs import importShape
            importShape()

        elif job == 'cluster':
            from abstractPatch import cluster

            dbDir = join(DATA_PATH, 'redis')
            startDB(dbDir, "6399", "ALLdumps-gumInput.rdb")
            startDB(dbDir, "6380", "clusterl0-gumInputALL.rdb")

            cluster(join(DATA_PATH,'shapes'),join(DATA_PATH, 'pairs'),'shapes')

        elif job =='actionPairs':
            from pairs import actionPairs
            actionPairs()

        elif job =='importActionPairs':
            from pairs import importAction
            importAction()

        elif job == 'clusterActions':
            from abstractPatch import cluster

            dbDir = join(DATA_PATH, 'redis')
            startDB(dbDir, "6399", "ALLdumps-gumInput.rdb")
            startDB(dbDir, "6380", "clusterl1-gumInputALL.rdb")

            cluster( join(DATA_PATH, 'actions'),join(DATA_PATH, 'pairsAction'),'actions')

        elif job == 'tokenPairs':
            from pairs import tokenPairs
            tokenPairs()

        elif job == 'importTokenPairs':
            from pairs import importToken
            importToken()

        elif job == 'clusterTokens':
            from abstractPatch import cluster

            dbDir = join(DATA_PATH, 'redis')
            startDB(dbDir, "6399", "ALLdumps-gumInput.rdb")
            startDB(dbDir, "6380", "clusterl2-gumInputALL.rdb")
            cluster(join(DATA_PATH, 'tokens'), join(DATA_PATH, 'pairsToken'),'tokens')

        #TODO optional
        elif job == 'compareTokens':
            roots = listdir(join(DATA_PATH,'pairsToken'))
            import redis
            port = '6380'
            dbDir = join(DATA_PATH, 'redis')
            startDB(dbDir, port, "clusterl2-gumInputALL.rdb")

            redis_db = redis.StrictRedis(host="localhost", port=port, db=0)

            # redis_pool = redis.ConnectionPool(host="localhost", port=port)

            # redis_db = redis.Redis(connection_pool=redis_pool,db=0)

            keys = redis_db.scan(0, match='*', count='1000000')
            keys = [i.decode() for i in keys[1]]


            from tokens import simiCore
            for key in keys:
                simiCore(key)
            # parallelRun(simiCore,keys)

            print()



        elif job =='stats':
            from stats import statsNormal
            statsNormal(True)
        elif job == 'test':

            # if not isfile(join(DATA_PATH, 'patchPatterns.pickle')):
            import redis
            redis_db = redis.StrictRedis(host="localhost", port=6399, db=0)

            # redis_pool = redis.ConnectionPool(host="localhost", port=port)

            # redis_db = redis.Redis(connection_pool=redis_pool,db=0)


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
            matches['commit'] = matches['file'].apply(lambda x: x.split('_')[1])
            matches['hunk'] = matches['pairs_key'].apply(lambda x: x.split('/')[2].split('_')[-1])
            matches['fileName'] = matches['pairs_key'].apply(lambda x: '_'.join(x.split('/')[2].split('_')[:-1]))
            # matches[matches['size'] > 1]
            save_zipped_pickle(matches, join(DATA_PATH, 'matches.pickle'))
            test = matches.sort_values(by=['fileName', 'hunk'])[['root', 'size', 'fileName']]
            df = test.groupby(by=['fileName'], as_index=False).agg(lambda x: x.tolist())



            df['root'] = df['root'].apply(lambda x: ','.join(x))
            df['size'] = df['size'].apply(lambda x: ','.join(x))

            df = df.reindex(df.root.sort_values().index)
            roots = df.root.value_counts().loc[lambda x: x == 1].reset_index(name='count')['index']
            multipleroots = df[~df.root.isin(roots)]

            patterns = multipleroots.groupby(by=['root', 'size'], as_index=False).agg(lambda x: x.tolist())
                # save_zipped_pickle(patterns, join(DATA_PATH, 'patchPatterns.pickle'))
            # else:
            #     patterns = load_zipped_pickle(join(DATA_PATH, 'patchPatterns.pickle'))
            #     matches = load_zipped_pickle(join(DATA_PATH, 'matches.pickle'))

            patterns2verify = patterns[patterns.fileName.str.len() > 1]


            def fileList(source):
                matches = []
                for root, dirnames, filenames in os.walk(source):
                    for filename in filenames:
                        # if filename.endswith(('.txt')):
                            matches.append(filename)
                return matches
            # if not isfile(join(DATA_PATH,'shapePatchFiles')):
            def check(x):
                root = x['root']
                size = x['size']

                roots = root.split(',')
                sizes = size.split(',')
                res = []
                for r,s in zip(roots,sizes):
                    fileNames = x['fileName']
                    path = join(DATA_PATH,'shapes',r,s)
                    if isdir(path):
                        pairs = fileList(path)
                        pairs
                        filenames = list(set([re.split('.txt_[0-9]+', i)[0] + '.txt' for i in pairs]))
                        res.append( np.all([f in filenames for f in fileNames]))
                    else:
                        res.append( False)
                return np.all(res)
            patterns2verify['check'] = patterns2verify.apply(lambda x:check(x),axis=1)
            patterns2verify = patterns2verify[patterns2verify.check]

            def clusterList(source,f):
                matches = []
                for root, dirnames, filenames in os.walk(source):
                    for filename in filenames:
                        if filename.startswith(f):
                            matches.append(root.split('/')[-1])
                            # break
                return matches

            def cluster(x):
                root = x['root']
                size = x['size']

                roots = root.split(',')
                sizes = size.split(',')
                res = []
                fileNames = x['fileName']
                for fn in fileNames:
                    fCluster = []
                    for r,s in zip(roots,sizes):
                        path = join(DATA_PATH,'shapes',r,s)
                        if isdir(path):
                            clusters = clusterList(path,fn)
                            fCluster.extend(clusters)
                        else:
                            res.append( False)
                    res.append(tuple(fCluster))
                return res


            patterns2verify['cluster'] = patterns2verify.apply(lambda x: cluster(x), axis=1)


            def checkCluster(x):
                res = dict()
                for k,v in Counter(x).items():
                    if v>1:
                        res[k] = v
                return res



            patterns2verify['clusters'] = patterns2verify.cluster.apply(lambda x: checkCluster(x))
            patterns2verify = patterns2verify[patterns2verify.clusters != {}]
            lines = []
            patches = []
            def exportClusters(x):
                clusters = x['clusters']
                cluster = x['cluster']
                fileName = x['fileName']
                for k, v in clusters.items():
                    idx = [index for index, value in enumerate(cluster) if value == k]
                    files = [fileName[i] for i in idx]
                    patches.extend(files)
                    lines.append(str(x['root'])+str(x['size'])+str(k) + ','.join(files))



            patterns2verify.apply(lambda x:exportClusters(x),axis=1)
            with open('clusters2export','w')as f:
                f.writelines('\n'.join(lines))

            patterns2verify.to_csv('patterns2verify.csv', index=None, header=None, sep=';')

                # save_zipped_pickle(patches,join(DATA_PATH,'shapePatchFiles'))
            # else:
            #     patches = load_zipped_pickle(join(DATA_PATH,'shapePatchFiles'))
            #actions


            shapes =matches[matches.fileName.isin(patches)]
            test = shapes.sort_values(by=['fileName', 'hunk'])[['root', 'size', 'fileName']]
            df = test.groupby(by=['fileName'], as_index=False).agg(lambda x: x.tolist())
            # patterns2verify.fileName = patterns2verify.fileName.apply(lambda x: ','.join(x))
            df['root'] = df['root'].apply(lambda x: ','.join(x))
            df['size'] = df['size'].apply(lambda x: ','.join(x))

            df = df.reindex(df.root.sort_values().index)
            roots = df.root.value_counts().loc[lambda x: x == 1].reset_index(name='count')['index']
            multipleroots = df[~df.root.isin(roots)]

            patterns = multipleroots.groupby(by=['root', 'size'], as_index=False).agg(lambda x: x.tolist())

            patterns2verify = patterns[patterns.fileName.str.len() > 1]



            def check(x):
                root = x['root']
                size = x['size']

                roots = root.split(',')
                sizes = size.split(',')
                res = []
                for r, s in zip(roots, sizes):
                    fileNames = x['fileName']
                    path = join(DATA_PATH, 'actions', r, s)
                    if isdir(path):
                        pairs = fileList(path)
                        pairs
                        filenames = list(set([re.split('.txt_[0-9]+', i)[0] + '.txt' for i in pairs]))
                        res.append(np.all([f in filenames for f in fileNames]))
                    else:
                        res.append(False)
                return np.all(res)


            patterns2verify['check'] = patterns2verify.apply(lambda x: check(x), axis=1)
            patterns2verify = patterns2verify[patterns2verify.check]


            def clusterList(source, f):
                matches = []
                for root, dirnames, filenames in os.walk(source):
                    for filename in filenames:
                        if filename.startswith(f):
                            matches.append(tuple(root.split('/')[-2:]))
                            # break
                return matches


            def cluster(x):
                root = x['root']
                size = x['size']

                roots = root.split(',')
                sizes = size.split(',')
                res = []
                fileNames = x['fileName']
                for fn in fileNames:
                    fCluster = []
                    for r, s in zip(roots, sizes):
                        path = join(DATA_PATH, 'actions', r, s)
                        if isdir(path):
                            clusters = clusterList(path, fn)
                            fCluster.extend(clusters)
                        else:
                            res.append(False)
                    res.append(tuple(fCluster))
                return res


            patterns2verify['cluster'] = patterns2verify.apply(lambda x: cluster(x), axis=1)


            def checkCluster(x):
                res = dict()
                for k, v in Counter(x).items():
                    if v > 1:
                        res[k] = v
                return res


            patterns2verify['clusters'] = patterns2verify.cluster.apply(lambda x: checkCluster(x))
            patterns2verify = patterns2verify[patterns2verify.clusters != {}]
            lines = []
            patches = []


            def exportClusters(x):
                clusters = x['clusters']
                cluster = x['cluster']
                fileName = x['fileName']
                for k, v in clusters.items():
                    idx = [index for index, value in enumerate(cluster) if value == k]
                    files = [fileName[i] for i in idx]
                    patches.extend(files)
                    lines.append(str(x['root']) + str(x['size']) + str(k) + ','.join(files))


            patterns2verify.apply(lambda x: exportClusters(x), axis=1)
            lines

            # counts = pd.DataFrame(matches.file.value_counts())
            # counts.reset_index(inplace=True)
            # counts.columns = ['file','count']
            # counts
            # counts[counts['count'] == 1]
            # files = counts[counts['count'] == 1].file.values.tolist()
            #
            # keysToExport = matches[matches.file.isin(files)][['hunks']]
            # keysToExport.rename(columns={'hunks': 'pairs_key'}, inplace=True)
            # save_zipped_pickle(keysToExport,join(DATA_PATH,'singleHunks'))

        elif job =='bug':

            if isfile(join(DATA_PATH,'studyBugReports.pickle')):
                studyBugReports = load_zipped_pickle(join(DATA_PATH,'studyBugReports.pickle'))
            else:
                brs = load_zipped_pickle(join(DATA_PATH, args.subject + "bugReportsComplete.pickle"))
                commits = load_zipped_pickle(join(DATA_PATH, 'singleBR.pickle'))


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
                matches['commit'] = matches['file'].apply(lambda x: x.split('_')[1])

                subjects = pd.read_csv(join(DATA_PATH, 'subjects.csv'))

                def getBID(x):
                    try:
                        if x['repo'].endswith('.git'):
                            return None
                        subject = subjects.query("Repo == '{0}'".format(x['repo'])).Subject.tolist()[0]
                        bids = commits.query("commit.str.startswith('{0}') and project== '{1}'".format(x['commit'],subject)).bid.tolist()
                        return bids[0]
                    except Exception as e:
                        logging.error(e)

                matches['bid'] = matches.apply(lambda x:getBID(x),axis=1)



                subjects
                # res = pd.merge(matches, brs, on=['bid'])
                save_zipped_pickle(matches, join(DATA_PATH, 'studyDataset.pickle'))
                studyBugReports = brs[brs.bid.isin(matches.bid.unique())]
                save_zipped_pickle(studyBugReports,join(DATA_PATH,'studyBugReports.pickle'))
            if isfile(join(DATA_PATH,'studyBR_DTM_index')):
                brIndexes = load_zipped_pickle(join(DATA_PATH,'studyBR_DTM_index'))
                bugDTM = load_zipped_pickle(join(DATA_PATH, 'studyBR_DTM'))
                vectorDF = load_zipped_pickle(join(DATA_PATH,'studyBR_vector'))
                matches = load_zipped_pickle( join(DATA_PATH, 'studyDataset.pickle'))
            else:
                studyBugReports['description'] = studyBugReports['description'].fillna("")
                studyBugReports['sumDesc'] = studyBugReports['summary'] +studyBugReports['description']
                # corpus['sumDesc'] = corpus['summary'] + corpus['desc']
                # from common.preprocessing import
                # result, aVector = getVectorAndDtm(corpus, 'summary')
                from common.preprocessing import calculateTfIdfNLList

                corpusBug = studyBugReports['sumDesc'].values.tolist()
                from common.preprocessing import preprocessingNL

                preCorpusBug = list(map(preprocessingNL, corpusBug))

                v = calculateTfIdfNLList(preCorpusBug)
                bugDTM = v.transform(preCorpusBug)
                bugDTM
                save_zipped_pickle(bugDTM, join(DATA_PATH, 'studyBR_DTM'))
                brIndexes = studyBugReports['bid'].values.tolist()

                save_zipped_pickle(brIndexes,join(DATA_PATH,'studyBR_DTM_index'))
            # from sklearn.metrics.pairwise import cosine_similarity
            # cosine_similarity(bugDTM[11701], bugDTM[11111])
                vectorDF = pd.DataFrame(columns=['bid','dtm'])
                # idx = 0
                for idx, val in enumerate(brIndexes):
                    vectorDF.loc[idx] = [val,bugDTM[idx]]
                vectorDF

                save_zipped_pickle(vectorDF,join(DATA_PATH,'studyBR_vector'))

            matches
            if isfile(join(DATA_PATH,'study_clusters')):
                clustersDF = load_zipped_pickle(join(DATA_PATH,'study_clusters'))
            else:
                clustersDF = pd.DataFrame(columns=['cid','type','members'])
                idx = 0
                def statsCore(cs,type):
                    global idx

                    cs = [i for i in cs if not (i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith('closure-compiler.git') or i.startswith('joda-time.git') or i.startswith('mockito.git'))]
                    # print('Cluster %s : member size %s' % (shape+"-"+size +"-"+cluster, len(cs)))
                    if len(cs)>0:
                        if token is None:
                            if action is None:
                                t = shape + "-" + size + "-" + cluster

                                clustersDF.loc[idx] = [t,type,cs]
                                idx = idx+1
                            else:
                                t = shape + "-" + size + "-" + cluster + "-" + action#, len(cs)
                                clustersDF.loc[idx] = [t, type, cs]
                                idx = idx + 1
                        else:
                            # clusterSize = len(cs)
                            # if clusterSize > 0:
                            #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
                            t = shape + "-" + size + "-" + cluster + "-" + action + "-" + token #, clusterSize
                            clustersDF.loc[idx] = [t, type, cs]
                            idx = idx + 1

                for type in ['tokens','actions','shapes']:
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
                                    statsCore(cs,'shapes')
                                else:
                                    # level3
                                    for action in cs:
                                        if action.startswith('.'):
                                            continue
                                        tokens = listdir(join(shapesPath, shape, size, cluster, action))
                                        if shapesPath.endswith('actions'):
                                            statsCore(tokens,'actions')
                                        else:
                                            for token in tokens:
                                                if token.startswith('.'):
                                                    continue
                                                cs = listdir(join(shapesPath, shape, size, cluster, action, token))
                                                statsCore(cs,'tokens')

                clustersDF
                save_zipped_pickle(clustersDF,join(DATA_PATH,'study_clusters'))
                clustersDF

                # selected = clustersDF[clustersDF.type =='shapes']


                from sklearn.metrics.pairwise import cosine_similarity
                # cosine_similarity(bugDTM[11701], bugDTM[11111])
                def getSimilarity(x):
                    try:
                        if len(x) == 1:
                            return [1]
                        else:
                            filenames = list(set([re.split('.txt_[0-9]+', i)[0] for i in x]))
                            if len(filenames) == 1:
                                return [1]
                            else:
                                bids2Compare = [matches[matches.file.str.startswith(fn)].bid.unique()[0] for fn in filenames]

                                pairs = list(itertools.combinations(bids2Compare, 2))
                                pairs
                                res = []
                                for p in pairs:
                                    p
                                    simi =cosine_similarity(vectorDF[vectorDF.bid == p[0]].iloc[0].dtm,vectorDF[vectorDF.bid == p[1]].iloc[0].dtm)
                                    res.append(simi[0][0])
                                return res
                    except Exception as e:
                        logging.error(e)


                # import swifter
                clustersDF['simi'] =clustersDF.members.apply(lambda x:getSimilarity(x))
                save_zipped_pickle(clustersDF,join(DATA_PATH,'study_clusters'))

            clustersDF

            shapes = clustersDF[clustersDF.type == 'shapes']
            actions = clustersDF[clustersDF.type == 'actions']
            tokens = clustersDF[clustersDF.type == 'tokens']



            # shapes
            # yList = [list(itertools.chain.from_iterable(shapes.simi.values.tolist())),
            # list(itertools.chain.from_iterable(actions.simi.values.tolist())),
            # list(itertools.chain.from_iterable(tokens.simi.values.tolist()))]
            # colNames = ['shapes','actions','tokens']
            # plotBox(yList, colNames, 'bugReport' + '.pdf', True)
            for ds in [shapes,actions,tokens]:
                ds['ms'] = ds.members.str.len()
                ds.sort_values(by=['ms'], ascending=False,inplace=True)
                top10  = ds.head(9)

                colNames = top10.cid.values.tolist()

                yList = yList = top10.simi.values.tolist()
                colNames.insert(0,'ALL')
                yList.insert(0,list(itertools.chain.from_iterable(ds.simi.values.tolist())))
                type = ds.type.iloc[0]
                from common.commons import plotBox
                plotBox(yList,colNames,type+'.pdf',True)

        elif job == 'defects4j':
            from stats import defects4jStats
            defects4jStats()



















    except Exception as e:
        logging.error(e)

from common.commons import *


if __name__ == '__main__':


    try:
        args = getRun()
        setLogg()


        setEnv(args)

        job = args.job
        # job = 'clusterActions'
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

        if job == 'clone':
            from commitCollector import *

            caseClone(args.subject)
        elif job == 'collect':
            from commitCollector import *

            caseCollect(args.subject)
        elif job == 'fix':
            from filterBugFixingCommits import caseFix

            caseFix(args.subject)

        elif job =='getSingleFix':
            for i in listdir(COMMIT_DFS):
                commits = load_zipped_pickle(join(COMMIT_DFS,i))

                singleFix = commits.fix.value_counts().loc[lambda x: x == 1].reset_index(name='count')['index']

                singleCommits = commits[commits.fix.isin(singleFix)]
                singleCommits['fix'] = singleCommits.fix.apply(lambda x: x.strip().upper())
                save_zipped_pickle(singleCommits,join(COMMIT_DFS,i))

        elif job =='brDownload':
            from bugReportDownloader import caseBRDownload
            caseBRDownload(args.subject)
        elif job =='brParser':
            from bugReportParser import step1
            step1(args.subject)
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
                parallelRun(prepareFiles,workList)

        elif job =='calculatePairs':
            roots = listdir(join(DATA_PATH,'EnhancedASTDiffgumInput'))
            for root in roots:
                if root.startswith('.'):
                    continue
                sizes = listdir(join(DATA_PATH,'EnhancedASTDiffgumInput',root))
                for sf in sizes:
                    if sf.startswith('.'):
                        continue
                    files = listdir(join(DATA_PATH,'EnhancedASTDiffgumInput',root,sf))

                    if len(files)>1:
                        files
                        indexCompared = []
                        if not os.path.exists(join(DATA_PATH, 'pairs', root)):
                            os.mkdir(join(DATA_PATH, 'pairs', root))

                        with open(join(DATA_PATH, 'pairs', root, sf + '.index'), 'w') as out:
                            # csv_out = csv.writer(out)

                            for idx, val in enumerate(files):

                                out.write(str(idx) + ',' + val + '\n')
                                indexCompared.append(str(idx))

                        pairs = list(itertools.combinations(indexCompared,2))
                        pairs
                        # import csv



                        with open(join(DATA_PATH,'pairs',root,sf+'.txt'),'w') as out:
                            # csv_out = csv.writer(out)
                            for row in pairs:
                                a, b = row
                                out.write(a + ','+b+'\n')
        elif job == 'importShapesPairs':

            dbDir = join(DATA_PATH, 'redis')

            portInner = '6380'
            cmd = "bash " + dbDir + "/" + "startServer.sh " + dbDir + " clusterl0-gumInputALL.rdb " + " " + portInner;

            o, e = shellGitCheckout(cmd)
            ping = "redis-cli -p 6380 ping"
            o, e = shellGitCheckout(ping)
            m = re.search('PONG', o)

            while not m:
                time.sleep(10)
                logging.info('Waiting for checkout')
                m = re.search('PONG', o)

            import redis
            pairsShapes = join(DATA_PATH, 'pairs')
            redis_db = redis.StrictRedis(host="localhost", port=portInner, db=1)
            pairs = get_filepaths(pairsShapes,'.txt')
            for pair in pairs:
                split = pair.split("/")
                shapeName = ''#split[-3]
                sizeCluster = split[-2]
                actionCluster = split[-1].replace('.txt','')
                cmd ="bash " + join(DATA_PATH,'redisSingleImport.sh') + " " +  pair + " 6380 " +sizeCluster+"-"+actionCluster ;

                o,e = shellGitCheckout(cmd)
                print(o)
                indexFile = pair.replace('.txt','.index')
                with open(indexFile,'r') as iFile:
                    idx =iFile.readlines()
                for i in idx:
                    k,v = i.split(',')
                    key = shapeName + "-" + sizeCluster+"-" +actionCluster+"-" + k
                    redis_db.set(key,v.strip())

        elif job == 'cluster':
            from abstractPatch import cluster
            cluster(join(DATA_PATH,'gumInput'),join(DATA_PATH,'shapes'),join(DATA_PATH,'EnhancedASTDiffgumInput'),join(DATA_PATH, 'pairs'),'shapes')

        elif job =='actionPairs':
            shapes = listdir(join(DATA_PATH,'shapes'))
            shapes = [f for f in shapes if isdir(join(DATA_PATH,'shapes',f))]
            shapes
            for shape in shapes:
                sizes = listdir(join(DATA_PATH, 'shapes',shape))
                sizes = [f for f in  sizes if isdir(join(DATA_PATH, 'shapes', shape,f))]
                for sf in sizes:
                    if sf.startswith('.'):
                        continue
                    clusters = listdir(join(DATA_PATH, 'shapes', shape,sf))
                    for cluster in clusters:
                        if cluster.startswith('.'):
                            continue
                        files = listdir(join(DATA_PATH, 'shapes', shape, sf,cluster))
                        indexCompared = []
                        if not os.path.exists(join(DATA_PATH, 'pairsAction', shape,sf)):
                            os.makedirs(join(DATA_PATH, 'pairsAction', shape,sf))

                        with open(join(DATA_PATH, 'pairsAction', shape,sf,cluster + '.index'), 'w') as out:
                            # csv_out = csv.writer(out)

                            for idx, val in enumerate(files):
                                out.write(str(idx) + ',' + val + '\n')
                                indexCompared.append(str(idx))

                        pairs = list(itertools.combinations(indexCompared, 2))

                        with open(join(DATA_PATH, 'pairsAction', shape,sf, cluster + '.txt'), 'w') as out:
                            # csv_out = csv.writer(out)
                            for row in pairs:
                                a, b = row
                                out.write(a + ',' + b + '\n')

        elif job =='importActionPairs':

            dbDir = join(DATA_PATH,'redis')

            portInner = '6380'
            cmd = "bash "+dbDir + "/" + "startServer.sh " +dbDir+ " clusterl1-gumInputALL.rdb "+  " " + portInner ;

            o,e = shellGitCheckout(cmd)
            ping = "redis-cli -p 6380 ping"
            o, e = shellGitCheckout(ping)
            m = re.search('PONG', o)

            while not m:
                time.sleep(10)
                logging.info('Waiting for checkout')
                m = re.search('PONG', o)

            import redis
            #import pairs
            pairsAction = join(DATA_PATH, 'pairsAction')
            redis_db = redis.StrictRedis(host="localhost", port=portInner, db=1)
            pairs = get_filepaths(pairsAction,'.txt')
            for pair in pairs:
                 split = pair.split("/")
                 shapeName = split[-3]
                 shapeSize = split[-2]
                 cluster = split[-1].replace('.txt','')
                 cmd ="bash " + join(DATA_PATH,'redisSingleImport.sh') + " " +  pair + " 6380 " +  shapeName +"-"+shapeSize +"-"+cluster ;#+, portInner,f.getName()+"-"+pair.getName().split("\\.")[0]);
            
                 o,e = shellGitCheckout(cmd)
                 print(o)
                 indexFile = pair.replace('.txt','.index')
                 with open(indexFile,'r') as iFile:
                     idx =iFile.readlines()
                 for i in idx:
                     k,v = i.split(',')
                     key = shapeName +"-"+shapeSize +"-"+cluster+"-" + k
                     redis_db.set(key,v.strip())

            # redis_db = redis.StrictRedis(host="localhost", port=portInner, db=0)
            # keys = redis_db.scan(0, match='*', count='100000000')
            #
            # workList = [f.decode() for f in keys[1]]
            # workList
            #
            # javaClassPAth = '/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/bin/java -Dfile.encoding=UTF-8 -classpath "/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/charsets.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/deploy.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/cldrdata.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/dnsns.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/jaccess.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/jfxrt.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/localedata.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/nashorn.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/sunec.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/sunjce_provider.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/sunpkcs11.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/ext/zipfs.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/javaws.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/jce.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/jfr.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/jfxswt.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/jsse.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/management-agent.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/plugin.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/resources.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/jre/lib/rt.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/lib/ant-javafx.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/lib/dt.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/lib/javafx-mx.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/lib/jconsole.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/lib/packager.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/lib/sa-jdi.jar:/Library/Java/JavaVirtualMachines/jdk1.8.0_181.jdk/Contents/Home/lib/tools.jar:/Users/anil.koyuncu/projects/fixminer-all/fixminer_source/target/classes:/Users/anil.koyuncu/.m2/repository/org/javatuples/javatuples/1.2/javatuples-1.2.jar:/Users/anil.koyuncu/projects/fixminer-all/simple-utils/target/classes:/Users/anil.koyuncu/.m2/repository/org/apache/poi/poi/3.12/poi-3.12.jar:/Users/anil.koyuncu/.m2/repository/commons-codec/commons-codec/1.9/commons-codec-1.9.jar:/Users/anil.koyuncu/.m2/repository/org/apache/poi/poi-ooxml/3.12/poi-ooxml-3.12.jar:/Users/anil.koyuncu/.m2/repository/org/apache/poi/poi-ooxml-schemas/3.12/poi-ooxml-schemas-3.12.jar:/Users/anil.koyuncu/.m2/repository/org/apache/xmlbeans/xmlbeans/2.6.0/xmlbeans-2.6.0.jar:/Users/anil.koyuncu/.m2/repository/stax/stax-api/1.0.1/stax-api-1.0.1.jar:/Users/anil.koyuncu/.m2/repository/net/sourceforge/jexcelapi/jxl/2.6.12/jxl-2.6.12.jar:/Users/anil.koyuncu/.m2/repository/log4j/log4j/1.2.14/log4j-1.2.14.jar:/Users/anil.koyuncu/.m2/repository/com/typesafe/akka/akka-actor_2.11/2.4.11/akka-actor_2.11-2.4.11.jar:/Users/anil.koyuncu/.m2/repository/org/scala-lang/scala-library/2.11.8/scala-library-2.11.8.jar:/Users/anil.koyuncu/.m2/repository/com/typesafe/config/1.3.0/config-1.3.0.jar:/Users/anil.koyuncu/.m2/repository/org/scala-lang/modules/scala-java8-compat_2.11/0.7.0/scala-java8-compat_2.11-0.7.0.jar:/Users/anil.koyuncu/projects/fixminer-all/gumtree/core/target/classes:/Users/anil.koyuncu/.m2/repository/com/github/mpkorstanje/simmetrics-core/3.0.3/simmetrics-core-3.0.3.jar:/Users/anil.koyuncu/.m2/repository/com/google/guava/guava/18.0/guava-18.0.jar:/Users/anil.koyuncu/.m2/repository/net/sf/trove4j/trove4j/3.0.3/trove4j-3.0.3.jar:/Users/anil.koyuncu/.m2/repository/com/google/code/gson/gson/2.3/gson-2.3.jar:/Users/anil.koyuncu/projects/fixminer-all/gumtree/gen.jdt/target/classes:/Users/anil.koyuncu/.m2/repository/org/eclipse/core/runtime/3.10.0-v20140318-2214/runtime-3.10.0-v20140318-2214.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/osgi/3.10.0-v20140606-1445/osgi-3.10.0-v20140606-1445.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/equinox/common/3.6.200-v20130402-1505/common-3.6.200-v20130402-1505.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/core/jobs/3.6.0-v20140424-0053/jobs-3.6.0-v20140424-0053.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/equinox/registry/3.5.400-v20140428-1507/registry-3.5.400-v20140428-1507.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/equinox/preferences/3.5.200-v20140224-1527/preferences-3.5.200-v20140224-1527.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/core/contenttype/3.4.200-v20140207-1251/contenttype-3.4.200-v20140207-1251.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/equinox/app/1.3.200-v20130910-1609/app-1.3.200-v20130910-1609.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/birt/runtime/org.eclipse.core.resources/3.10.0.v20150423-0755/org.eclipse.core.resources-3.10.0.v20150423-0755.jar:/Users/anil.koyuncu/.m2/repository/org/eclipse/tycho/org.eclipse.jdt.core/3.12.2.v20161117-1814/org.eclipse.jdt.core-3.12.2.v20161117-1814.jar:/Users/anil.koyuncu/.m2/repository/org/slf4j/slf4j-api/1.7.7/slf4j-api-1.7.7.jar:/Users/anil.koyuncu/.m2/repository/ch/qos/logback/logback-classic/1.1.2/logback-classic-1.1.2.jar:/Users/anil.koyuncu/.m2/repository/ch/qos/logback/logback-core/1.1.2/logback-core-1.1.2.jar:/Users/anil.koyuncu/.m2/repository/junit/junit/4.11/junit-4.11.jar:/Users/anil.koyuncu/.m2/repository/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar:/Users/anil.koyuncu/.m2/repository/redis/clients/jedis/2.8.1/jedis-2.8.1.jar:/Users/anil.koyuncu/.m2/repository/org/apache/commons/commons-pool2/2.4.2/commons-pool2-2.4.2.jar:/Users/anil.koyuncu/.m2/repository/org/apache/commons/commons-text/1.3/commons-text-1.3.jar:/Users/anil.koyuncu/.m2/repository/org/apache/commons/commons-lang3/3.7/commons-lang3-3.7.jar:/Users/anil.koyuncu/.m2/repository/com/rabbitmq/amqp-client/4.0.0/amqp-client-4.0.0.jar:/Applications/IntelliJ IDEA CE.app/Contents/lib/idea_rt.jar"'
            # def run(aKey):
            #     cmd = javaClassPAth+" -jar /Users/anil.koyuncu/projects/fixminer-all/fixminer_source/target/FixPatternMiner-0.0.1-SNAPSHOT-jar-with-dependencies.jar " + aKey + " action"
            #     o,e = shellGitCheckout(cmd)
            #     # logging.info(o)
            #     # logging.error(e)
            #
            # parallelRun(run,workList)

        elif job == 'clusterActions':
            from abstractPatch import cluster

            cluster(join(DATA_PATH, 'gumInput'), join(DATA_PATH, 'actions'), join(DATA_PATH, 'EnhancedASTDiffgumInput'),
                    join(DATA_PATH, 'pairsAction'),'actions')

        elif job == 'tokenPairs':
            shapes = listdir(join(DATA_PATH, 'actions'))
            shapes = [f for f in shapes if isdir(join(DATA_PATH, 'actions', f))]

            for shape in shapes:
                sizes = listdir(join(DATA_PATH, 'actions', shape))
                sizes = [f for f in sizes if isdir(join(DATA_PATH, 'actions', shape, f))]
                for sf in sizes:
                    if sf.startswith('.'):
                        continue
                    actions = listdir(join(DATA_PATH, 'actions', shape, sf))
                    for action in actions:
                        files = listdir(join(DATA_PATH, 'actions', shape, sf,action))
                        indexCompared = []
                        if not os.path.exists(join(DATA_PATH, 'pairsToken', shape,sf)):
                            os.makedirs(join(DATA_PATH, 'pairsToken', shape,sf))

                        with open(join(DATA_PATH, 'pairsToken', shape, sf, action+ '.index'), 'w') as out:
                            # csv_out = csv.writer(out)

                            for idx, val in enumerate(files):
                                out.write(str(idx) + ',' + val + '\n')
                                indexCompared.append(str(idx))

                        pairs = list(itertools.combinations(indexCompared, 2))

                        with open(join(DATA_PATH, 'pairsToken', shape, sf,action + '.txt'), 'w') as out:
                            # csv_out = csv.writer(out)
                            for row in pairs:
                                a, b = row
                                out.write(a + ',' + b + '\n')

        elif job == 'importTokenPairs':

            dbDir = join(DATA_PATH, 'redis')

            portInner = '6380'
            cmd = "bash " + dbDir + "/" + "startServer.sh " + dbDir + " clusterl2-gumInputALL.rdb " + " " + portInner;

            o, e = shellGitCheckout(cmd)
            ping = "redis-cli -p 6380 ping"
            o, e = shellGitCheckout(ping)
            m = re.search('PONG', o)

            while not m:
                time.sleep(10)
                logging.info('Waiting for checkout')
                m = re.search('PONG', o)

            import redis
            pairsToken = join(DATA_PATH, 'pairsToken')
            redis_db = redis.StrictRedis(host="localhost", port=portInner, db=1)
            pairs = get_filepaths(pairsToken,'.txt')
            for pair in pairs:
                split = pair.split("/")
                shapeName = split[-3]
                sizeCluster = split[-2]
                actionCluster = split[-1].replace('.txt','')
                cmd ="bash " + join(DATA_PATH,'redisSingleImport.sh') + " " +  pair + " 6380 " +  shapeName + "-"+sizeCluster+"-"+actionCluster ;#+, portInner,f.getName()+"-"+pair.getName().split("\\.")[0]);

                o,e = shellGitCheckout(cmd)
                o
                indexFile = pair.replace('.txt','.index')
                with open(indexFile,'r') as iFile:
                    idx =iFile.readlines()
                for i in idx:
                    k,v = i.split(',')
                    key = shapeName + "-" + sizeCluster+"-" +actionCluster+"-" + k
                    redis_db.set(key,v.strip())

        elif job == 'clusterTokens':
            from abstractPatch import cluster

            cluster(join(DATA_PATH, 'gumInput'), join(DATA_PATH, 'tokens'), join(DATA_PATH, 'EnhancedASTDiffgumInput'),
                    join(DATA_PATH, 'pairsToken'),'tokens')



















    except Exception as e:
        logging.error(e)

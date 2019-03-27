from common.commons import *

DATA_PATH = os.environ["DATA_PATH"]
REPO_PATH = os.environ["REPO_PATH"]
def prepareFiles(t):
    try:
        sha, repoName = t

        shaOld = sha + '^'

        repo = join(REPO_PATH,repoName)
        gumInputRepo = join(DATA_PATH, 'gumInput', repoName)
        if not os.path.exists(join(gumInputRepo)):
            os.makedirs(gumInputRepo)

        cmd = 'git -C ' + repo + ' diff --name-only ' + shaOld + '..'+sha
        # lines = subprocess.check_output(cmd, shell=True)
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,encoding ='utf-8') as p:
            # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            output, errors = p.communicate()
        files = output.strip().split('\n')
        # nonJava = [f for f in files if not f.endswith('.java')]
        nonTest = [f for f in files if not re.search('test',f,re.I)]
        # if len(nonJava) > 0:
        #     logging.warning('Skipping commit %s',sha)
        #     return
        # if len(files) != 1:
        #     return

        nonTest = [f for f in files if not re.search('test', f, re.I) and f.endswith('java')]

        if len(nonTest) > 1:
            return

        cmd = 'git -C ' + repo + ' rev-parse --short=6 ' + shaOld
        # lines = subprocess.check_output(cmd, shell=True)
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf-8') as p:
            # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            output, errors = p.communicate()

        shaOld = output.strip()

        cmd = 'git -C ' + repo + ' rev-parse --short=6 ' + sha
        # lines = subprocess.check_output(cmd, shell=True)
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf-8') as p:
            # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            output, errors = p.communicate()

        sha = output.strip()

        if isinstance(nonTest, list):
            for file in nonTest:
                checkoutFiles(sha,shaOld, repoName, file)




        #lines = output.decode('latin-1')
        # print lines
        # original

    except Exception as e:
        print(e)
        #print('Skip ' + sha)
        # raise Exception(e)

def prepareFilesDefects4J(repo,repoName,shaOld):
    try:
        # sha, repoName = t

        sha = shaOld + '^'

        # repo = join(REPO_PATH,repoName)
        gumInputRepo = join(DATA_PATH, 'Defects4J2', repoName)
        if not os.path.exists(join(gumInputRepo)):
            os.makedirs(gumInputRepo)

        cmd = 'git -C ' + repo + ' diff --name-only ' + shaOld + '..'+sha
        # lines = subprocess.check_output(cmd, shell=True)
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True,encoding ='utf-8') as p:
            # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            output, errors = p.communicate()
        files = output.strip().split('\n')
        # nonJava = [f for f in files if not f.endswith('.java')]
        nonTest = [f for f in files if not re.search('test',f,re.I)]
        # if len(nonJava) > 0:
        #     logging.warning('Skipping commit %s',sha)
        #     return
        # if len(files) != 1:
        #     return

        nonTest = [f for f in files if not re.search('test', f, re.I) and f.endswith('java')]

        if len(nonTest) > 1:
            return

        cmd = 'git -C ' + repo + ' rev-parse --short=6 ' + shaOld
        # lines = subprocess.check_output(cmd, shell=True)
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf-8') as p:
            # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            output, errors = p.communicate()

        shaOld = output.strip()

        cmd = 'git -C ' + repo + ' rev-parse --short=6 ' + sha
        # lines = subprocess.check_output(cmd, shell=True)
        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf-8') as p:
            # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            output, errors = p.communicate()

        sha = output.strip()

        if isinstance(nonTest, list):
            for file in nonTest:
                checkoutFiles(sha,shaOld, repoName, file,repo)




        #lines = output.decode('latin-1')
        # print lines
        # original

    except Exception as e:
        print(e)
        #print('Skip ' + sha)
        # raise Exception(e)



def checkoutFiles(sha,shaOld,repoName, filePath,repo=None):
    try:
        # folderDiff = join(DATA_PATH, 'gumInput',repoName, 'DiffEntries')
        folderDiff = join(DATA_PATH, 'Defects4J2',repoName, 'DiffEntries')
        folderPrev = join(DATA_PATH, 'Defects4J2',repoName, 'prevFiles')
        folderRev = join(DATA_PATH, 'Defects4J2',repoName, 'revFiles')
        if not os.path.exists(folderDiff):
            os.mkdir(folderDiff)

        if not os.path.exists(folderPrev):
            os.mkdir(folderPrev)

        if not os.path.exists(folderRev):
            os.mkdir(folderRev)

        if repo is None:
            repo = join(REPO_PATH,repoName)


        savePath = filePath.replace('/','#')
        if not isfile(folderDiff + '/' + sha + '_' + shaOld + '_' + savePath.replace('.java', '.txt')):

            cmd = 'git -C ' + repo + ' diff -U ' + shaOld + ':' + filePath + '..' + sha + ':' + filePath  # + '> ' + folderDiff + '/' + sha + '_' + shaOld + '_' + savePath.replace('.java','.txt')
            # lines = subprocess.check_output(cmd, shell=True)
            # with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf-8') as p:
            #     # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            #     # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            #     output, errors = p.communicate()
            # if errors:
            #     # print(errors)
            #     raise FileNotFoundError
            output,errors = shellGitCheckout(cmd,'latin1')
            if errors:
                # print(errors)
                raise FileNotFoundError

            regex = r"@@\s\-\d+,*\d*\s\+\d+,*\d*\s@@ ?(.*\n)*"
            match = re.search(regex, output)
            if not match:
                return
                # print()
            not_matched, matched = output[:match.start()], match.group()
            numberOfHunks = re.findall('@@\s\-\d+,*\d*\s\+\d+,*\d*\s@@', matched)
            if len(numberOfHunks) == 0:
                return
            diffFile = shaOld + '\n' + matched.replace(' @@ ', ' @@\n')
            with open(folderDiff + '/' + sha + '_' + shaOld + '_' + savePath.replace('.java', '.txt'),
                      'w') as writeFile:
                writeFile.writelines(diffFile)



            cmd = 'git -C ' + repo + ' show ' + sha + ':' + filePath + '> ' + folderRev + '/' + sha + '_' + shaOld + '_' +savePath
            # lines = subprocess.check_output(cmd, shell=True)
            # with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True) as p:
            #     # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            #     # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            #     output, errors = p.communicate()
            # # lines = output.decode('latin-1')
            # # print lines
            # # original
            if errors:
                # print(errors)
                raise FileNotFoundError
            o,errors= shellGitCheckout(cmd,'latin1')
            cmd = 'git -C ' + repo + ' show ' + shaOld + ':' + filePath + '> ' + folderPrev + '/' + 'prev_'+sha + '_' + shaOld + '_' +savePath
            if errors:
                # print(errors)
                raise FileNotFoundError

            o,errors = shellGitCheckout(cmd,'latin1')
            if errors:
                # print(errors)
                raise FileNotFoundError
            # with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True) as p:
            #     # stdin={'file': PIPE, 'encoding': 'iso-8859-1', 'newline': False},
            #     # stdout={'file': PIPE, 'encoding': 'utf-8', 'buffering': 0, 'line_buffering': False}) as p:
            #     output, errors = p.communicate()
            #
            # if errors:
            #     print(errors)
            #     raise FileNotFoundError


            #return output
        # else:
            # print('Already done')
    except FileNotFoundError as fnfe:
        if isfile(folderRev + '/' + sha + '_' + shaOld + '_' +savePath):
            os.remove(folderRev + '/' + sha + '_' + shaOld + '_' +savePath)
        if isfile(folderPrev + '/' + 'prev_'+sha + '_' + shaOld + '_' +savePath):
            os.remove(folderPrev + '/' + 'prev_'+sha + '_' + shaOld + '_' +savePath)
        if isfile(folderDiff + '/' + sha + '_' + shaOld + '_' + savePath.replace('.java','.txt')):
            os.remove(folderDiff + '/' + sha + '_' + shaOld + '_' + savePath.replace('.java','.txt'))
        # print(fnfe)
        # raise Exception(fnfe)
    except Exception as e:
        # print(e)
        raise Exception(e)

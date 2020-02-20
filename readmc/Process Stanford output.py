# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on January 2020

@author: znhua
"""
import pandas as pd
import numpy as np

#### PART 1: Read in the Stanford Parser files and pre-process them
def splitDep(depStr):
    dep, headlex = depStr[:-2].split("(", 1)
    headi, lexi = headlex.split(", ")
    head, headPos = headi.rsplit("-", 1)
    lex, lexPos = lexi.rsplit("-", 1)
    return {'dep': dep, 'head': head, 'headPos': int(headPos), 
            'lex': lex, 'lexPos': int(lexPos)}
    
wkdir = "C:/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/data/output/"

modals = ["可能", "或许", "也许",
          "一定","肯定",
          "必须", "得",  "需要",  #"要",
          "肯", "可以", "可", 
          "会", "能够", "能", 
          "应该", "应", "该",
          "将", 
          #"别",
          ]
aspectSuffix = ["了", "过", "着"]
aspectPrefix = ["在", "没有", "没"]
neg = ["不", "没", "没有"]
wh = ("什么",  "啥", "谁", "哪", 
      "为什么", "为何", "干嘛", "干吗", 
      "怎么", "如何", "怎样", 
      "几", "多少")
"""
wtList = []
with open(wkdir+'wtall.txt', 'r', encoding = 'utf') as reader:
    for line in reader:
        if line != "\n":
            wtList.append((("r/r "+line).replace("\n","")).split(" "))

tdList = []
with open(wkdir+'tdall.txt', 'r', encoding = 'utf') as reader:
    deps = []
    for line in reader:    
        if line == "\n":
            tdList.append(deps)
            deps = []
        else:
            deps.append(splitDep(line))

wttd = list(zip(wtList,tdList))
"""
#### Open the tagging and dependency files
wttd = []
for f in ["Chang1",
          "Chang2",
          "ChangPNTrad",
          "TCCMTrad",
          "Tong",
          "Zhou1",
          "Zhou2",
          "Zhou3",
          "ZhouAssessment",
          "zhoudinner"
           # exclude ZhouNarrative, as it's mostly just the teacher asking questions
           ]:
    wtList = []
    with open(wkdir+f+'-wtall.txt', 'r', encoding = 'utf') as reader:
        for line in reader:
            if line != "\n":
                wtList.append((("r/r "+line).replace("\n","")).split(" "))
    
    tdList = []
    with open(wkdir+f+'-tdall.txt', 'r', encoding = 'utf') as reader:
        deps = []
        for line in reader:    
            if line == "\n":
                tdList.append(deps)
                deps = []
            else:
                deps.append(splitDep(line))
    
    wttd += list(zip(wtList,tdList))

#### Removes a few more items
wttdUse = []
for s in wttd:
    if s[0] != ['r/r', '=laughs/VV', './PU']:
        wttdUse.append(s)
wttd = wttdUse

#### This function lets you input a lex item, output sentences that contains it
#### getLex("送", "V")
def getLex(lex, lextag):
    for index, (wt,td) in enumerate(wttd[:]):
        wordFound = False
        ss = ""
        for i, wordTag in enumerate(wt):
            word=  wordTag.rsplit("/", 1)[0]
            tag = wordTag.rsplit("/", 1)[1]
            ss += word
            if word == lex and tag.startswith(lextag):
                wordFound = True
        if wordFound:
            print(index, ss, "\n")
            #print(td)


#### Some verbs are encoded such that the relation betweeen 
#### the verb and its complement should be switched around
#### In other words, the verbs are treated like auxiliaries
def checkXcomp(setDeps):
    actualHead = ''
    actualHeadPos = -1 # track whether a switch is needed
    #print("== old ==")
    
    # Go through all the dependencies in a sentence
    for deps in setDeps:
        # flag the original relations that need to be switched (actually, discarded)
        # in these instances, the "head" is the embedded verb
        # the "lex" is the verb in question (coded as an auxiliary), e.g. yao
        if deps['dep'] == 'xcomp' and deps['lex'] in ['要', '说', '去', '来', '请', '继续']:
            # assign new head
            actualHead = deps['lex']
            actualHeadPos = deps['lexPos']
            actualLex = deps['head']
            actualLexPos = deps['headPos']
            actualLexTag = deps['headTag']
            deps['discard'] = 'swappedXcomp-DISCARD' # flag it
        #print(deps)
        
    # If a switch is needed, create a new dependency entry with the "right" relations
    if actualHeadPos != -1:
        setDeps.append({
                'dep': 'xcomp',
                'head': actualHead,
                'lex': actualLex,
                'headPos': actualHeadPos,
                'lexPos': actualLexPos,
                'headTag': 'VV',
                'lexTag': actualLexTag,
                })
    #print("== new ==\t", actualHead, actualHeadPos)
    
    # After we have made the switch, we update all other dependencies 
    # that PRECEDE lex (now head) and are NOTATED AS DEPENDING on the embedded predicate (now lex)
    # Purpose: primarily to make sure that the subject is a dependent of the new head.
    # Assume that all lexical items that following lex/new head are still dependents of the embedded predicate
    for deps in setDeps:
        if actualHeadPos != -1:
            # if preceding X is dependent on embedded predicate
            # e.g. the subject
            if (deps['lexPos'] < actualHeadPos
                and deps['headPos'] == actualLexPos):
                deps['origHead'] = deps['head'] # for record-keeping
                deps['head'] = actualHead
                deps['headPos'] = actualHeadPos
            # if the preceding X is the head of the embedded predicate
            # e.g. <no example> but just in case
            if (deps['headPos'] < actualHeadPos 
                and deps['lexPos'] == actualLexPos): 
                deps['origLex'] = deps['lex'] # for record-keeping
                deps['lex'] = actualHead
                deps['lexPos'] = actualHeadPos
            # if a punctuation mark marks 
            # the embedded predicate as a dependent
            if (deps['dep'] != "root"
                and deps['headTag'] == "PU" # 
                and deps['lexPos'] == actualLexPos):
                deps['origLex'] = deps['lex'] # for record-keeping
                deps['lex'] = actualHead
                deps['lexPos'] = actualHeadPos
    return(setDeps)

# Some "complements" are marked as ccomps
# These might include parts of an A-x-A construction, or a A-de-ADJ
def checkCcomp(setDeps):
    # Create headLexs to track ccomps
    AxA = []
    headLexs = []
    for deps in setDeps:
        if deps['dep'] in ['ccomp', 
                                   # 'conj',
                                   #'dep'
               ]:
            if (
                (deps['head'] == deps['lex'][0] and deps['headPos'] == deps['lexPos']-2)
                or (deps['head'] == deps['lex'] and deps['headPos'] == deps['lexPos']-2)
                ):
                # A-x-AB or AB-x-AB, A = head, AB = lex
                # sometimes A-x-A gets coded as ccomp or conj
                # sometimes A-de-ADJ gets coded as ccomp 
                # store these in AxA. We fix these ccomps later
                deps['dep'] = 'AxA'
                AxA.append([deps['head'], deps['headPos'], deps['lex']])
            else:
                headLexs.append({'head': deps['head'], 
                'headPos': deps['headPos'], 
                'lex': deps['lex'], 
                'lexPos': deps['lexPos']})
            #for d in setDeps:
            #    print(d)
        # the Stanford parser codes the clausal complement of 告诉 as a 'dep'
        # so we need to fix that - code the complement as a ccomp
        if (deps['dep'] == 'dep' and deps['head'] == '告诉'
            and deps['lexPos'] > deps['headPos']):
            deps['origDep'] = 'dep'
            deps['dep'] = 'ccomp'
    
    # quick fix for A-x-A: we don't want the first A coded as a head anywhere.
    # For every AxA entry in AxA, go through the full set of dependencies
    for a in AxA:
        for deps in setDeps:
            # Find dependents whose head is the first A, like *zhi*-bu-zhidao
            if deps['head'] == a[0] and deps['headPos'] == a[1]:
                # Set the head to a[2], a[2] being the actual word, like zhidao
                deps['head'] = a[2] 
                
    # Now, for true ccomps
    # Go through the set of dependencies
    # find instances where the head verb has an object
    # Convert this to nsubject
    # This affects control verbs, for instance
    """
    for headLex in headLexs:
        dobjExists = False
        nsubjExists = False
        for deps in setDeps:
            if (deps['head'] == headLex['head'] and deps['headPos'] == headLex['headPos'] 
                and 'dobj' in deps.values()
                and headLex['lex'] != "是"
                ):
                dobjExists = True
                deps['origHead'] = headLex['head'] + "_"+ str(headLex['headPos'])
                # change the dependency type to a subject
                deps['dep'] = 'nsubj'
                # "switch" the head of this "subject" dependency to the embedded predicate
                deps['head'] = headLex['lex']
                deps['headPos'] = headLex['lexPos']
                ## For debugging
                #print("cc", 1)
                #print("obj\n", deps, "\n", printDeps(setDeps, headLex['head']))
            
            
            # find instances where the subordinate verb has a subject
            # no action necessary
            if (deps['head'] == headLex['lex'] and deps['headPos'] == headLex['lexPos'] 
                and 'nsubj' in deps.values()
                ):
                nsubjExists = True
                #print("sbj\n", deps, "\n", printDeps(setDeps, headLex['lex']))
                #print("sbj\n")
                #for dep in setDeps:
                #    print(dep)
   """

#### Annotate passives
def annotatePassives(vDeps):
    passiveVerbHeadPos = []
    for dep in vDeps:
        if dep['dep'] == 'auxpass':
            if dep['lexTag'] == 'LB': # long passive
                passiveVerbHeadPos.append(dep['headPos'])
    for headPos in passiveVerbHeadPos:
        for dep in vDeps:
            if dep['dep'] == 'nsubj' and dep['headPos'] == headPos:
                dep['dep'] = 'nsubjLB'

# To look at the details of a dep
def printDeps(deps, head):
    for dep in deps:
        if dep['head'] == head:
            print(dep)

# 知不知道
# yao NP-4 ... V-7 ... coded as dep(准备-7, 妈妈-4)
#if dep['dep'] == 'dep' and wt[dep['lexPos']][-2] == 'N':
#    dep['origDep'] = 'dep'
#    dep['dep'] = 'nsubj'

def assignEmbedding(setDeps):
    # At this point we have xcomp and ccomp to clean up dependencies
    # We want to indicate which dependencies are found in embedded contexts
    # and which ones are found in root contexts
    embedding = {}
    prohibitive = False
    for dep in setDeps:
        # Generate a list of embedded predicates and what predicate it is embedded by
        if (# we are looking for ccomp or xcomp
            'comp' in dep['dep'] 
            # we want to set aside the "discard" entries - these are the original ones with "errors"
            and 'discard' not in dep.keys()):
            embeddedPredPos = dep['lex'] + str(dep['lexPos'])
            embedding[embeddedPredPos] = dep['head']

    # At this point "embedding" contains a set of items that head a ccomp or xcomp    
    # get a list of items that are dependents of the embedded predicate, e.g. subject
    for dep in setDeps:
        # for every dependency, see what the head is
        headAndPos = dep['head']+str(dep['headPos'])
        # if the head is in the set of items in "embedding"
        if headAndPos in embedding.keys():
            # then add an entry saying what lex item embeds it
            dep['embeddedBy'] = embedding[headAndPos]
        else:
            # in the event the head and dependency is embedded by "root"
            dep['embeddedBy'] = 'root'
            # and if we have clear evidence that this is a prohibitive
            if dep['lex'] == '别' and dep['lexTag'] == 'AD':
                prohibitive = True
    
    return prohibitive

# Function to print list of items in a neat fashion
def prLs(listItem):
    for i in listItem:
        print(i)

def resetRoot(setDeps):
    # find root
    #prLs(setDeps)
    punctPos = -1
    reset = -1
    actualHead = ""
    actualHeadPos = -1
    actualHeadTag = ""
    
    for dep in setDeps:
        # the parser always designate 0 as the 'ROOT' 
        # and some lexical item as its dependent
        # If we find a lexical item that is in a root relation
        # then this is probably the root verb
        if dep['dep'].lower() == 'root':
            # but sometimes, this lexical item is actually a punctuation point, not a predicate
            if dep['lexTag'] in ['PU']:
                # We then save this fact -- the punctuation point and the position
                punctPos = dep['lexPos']
                #print(get1stVDaughter, rootPos)
                # We will look for the first verb that is dependent on this punctuation mark
                # and designate that verb as the root verb
    
    # In cases where the root's dependent is a punctuation point
    if punctPos != -1:
        # go through the set of dependencies again
        for dep in setDeps:
            # find a lexical item that depends on the punctuation point as its head
            if dep['headPos'] == punctPos:
                if reset == -1:
                    # if we haven't done anything to this dependency entry...
                    # Reset the dependency so it is now dependent on 0/'ROOT'
                    # and not the punctuation point
                    dep['dep'] = 'root'
                    dep['head'] = 'ROOT'
                    dep['headPos'] = 0
                    dep['headTag'] = 'root'
                    actualHead = dep['lex']
                    actualHeadPos = dep['lexPos']
                    actualHeadTag = dep['lexTag']
                    reset = 1
                else:
                    dep['head'] = actualHead
                    dep['headPos'] = actualHeadPos
                    dep['headTag'] = actualHeadTag
                    
    #return root, rootPos

#### This method is used to print certain dependencies, for debugging
def getDepRootComp(allVerbDeps, rootStatus, root, rootPos):
    print("rootStatus", rootStatus, "pred: ", root)
    # print relevant dependencies
    for dep2 in allVerbDeps:
        if dep2['head'] == root and dep2['headPos'] == rootPos:
            #print('abc\t', dep2)
            if 'nsubj' in dep2['dep']:
                print('sbj\t', dep2)
            if (dep2['lex'] in modals and
                ('aux:modal' in dep2['dep'] 
                or 'advmod' in dep2['dep']
                or 'dep' in dep2['dep'])
                and (dep2['lexTag'] not in ['DER', 'NN' ])
                ):
                # shoudl be aux:modal (not DER not ACL (会儿))
                # or advmod
                print('aux\t', dep2)
            if ((dep2['lex'] in aspectPrefix or dep2['lex'] in aspectSuffix) and 
                dep2['dep'] in ['aux:asp', 'advmod', 'neg']):
                # zhe, le = aux:asp, what about discourse le? (coding not consistent)
                # mei = neg of Verb
                # zai = advmod of verb
                print('asp\t', dep2)
            if (dep2['head'] in ['有'] and 
                dep2['headTag'][0] == ['V']
                ):
                print('you\t', dep2)
            if (dep2['lex'] in neg and 
                dep2['dep'] == 'neg'):
                print('neg\t', dep2)

    # if a dependency contains a dep, conj, ccomp
    # "save" the lexical item in embPred
    embPred = []
    for dep in allVerbDeps:
        if ( (dep['dep'] in ['dep', 'conj'] 
                or 'comp' in dep['dep'])
            and dep['head'] == root 
            and dep['headPos'] == rootPos
            and 'discard' not in dep.keys()):
            #print(dep)
            embedType = dep['dep']
            predLex = dep['lex']
            predPos = dep['lexPos']
            embPred.append([predLex, predPos, embedType])
    # Go through the "saved" items, then run the same algorithm on each of these items 
    # to see what their dependencies are
    for pred in embPred:
        predLex = pred[0]
        predPos = pred[1]
        embedType = pred[2]
        #print("yyyy: ", predLex)
        getDepRootComp(allVerbDeps, embedType+'/'+root, predLex, predPos)
    
#### PART 2: Extract the relevant dependencies and re-format them
#### Output: a dictionary. 
#### Key = index of a sentence
#### Values = List of lexical items - what its dependencies are, what is its head, what dependency it has with its head
#30 要不要出来 dep (yao, chulai)
# For each sentence, save it and its dependencies in sDeps under its index
sDeps = {}

for index, (wt,td) in enumerate(wttd[:]):
    sentence = ""
    endPunct = "."
    sDeps[index] = {}
    # this marks the sentence as a question
    if "?" in wt[-1]:
        endPunct = "?"
    
    # Step 1. Add syntactic categories
    for i, wordTag in enumerate(wt):
        word = wordTag.rsplit("/", 1)[0]
        tag = wordTag.rsplit("/", 1)[1]
        
        """
        if word in aspectPrefix and tag not in ["DER", "NN"]:
            print("=====\n", wt)
            print("=====\n", td)
        """
        # Add POS information
        for dep in td:
            #print("x\t", word, tag, dep)
            if (dep['lex'] == word and dep['lexPos'] == i):
                dep['lexTag'] = tag
            if (dep['head'] == word and dep['headPos'] == i):
                dep['headTag'] = tag
            if (dep['head'] == 'root'):
                dep['headTag'] = 'root'
        # Construct the full sentence
        sentence += word
    
    # Step 2. Generate all dependencies related to a verb, noun, preposition
    # Save them in "allVerbDeps"
    allVerbDeps = []
    for i, wordTag in enumerate(wt):
        word = wordTag.rsplit("/", 1)[0]
        tag = wordTag.rsplit("/", 1)[1]
        # We don't need dependencies relating to punctuation, for instance
        if tag[0] in ["V", "N", "P"] and word not in ['xxx', '[DEL]']:
            vDeps = []
            #print(i, '\t', wordTag)
            for dep in td:
                #print(word, tag[0], dep)
                if word in dep['head'] or word in dep['lex']:
                    vDeps.append(dep)
                    
            # Check for xcomp and fix xcomp, if necessary
            vDeps = checkXcomp(vDeps)
            
            # there will be repeated entries in vDeps - take them out
            for deps in vDeps:
                if deps not in allVerbDeps:
                    allVerbDeps.append(deps)
    
    annotatePassives(allVerbDeps)
    # Step 3. Find / Correct the root predicate in td
    resetRoot(allVerbDeps)
    """
    #rootTag = wt[rootPos]
    #print('a\n', prLs(allVerbDeps), '\nb')
    """
    # Step 4. Clean up the dependencies in allVerbDeps
    # Step 4a. Fix ccomps
    checkCcomp(allVerbDeps)
    # Step 4b. For each dependency, determine what predicate it is embedded under
    sDeps[index]['prohibitive'] = assignEmbedding(allVerbDeps)
    # Step 5. "Save" the cleaned-up dependencies in sDeps
    sDeps[index]['endPunct'] = endPunct
    sDeps[index]['setDeps'] = allVerbDeps
    sDeps[index]['sentence'] = sentence[1:]
    # Step 6. Check that the code is working properly
    # Step 6a. Display the relevant dependencies
    #getDepRootComp(allVerbDeps, 'root/root', root, rootPos)
    
    # Step 6b. Go through the verbs and print their dependencies
    ## Needed only for checking
    """
    for i, wordTag in enumerate(wt):
        word = wordTag.rsplit("/", 1)[0]
        tag = wordTag.rsplit("/", 1)[1]
        if tag[0] in ["V"] and word not in ['xxx', '[DEL]']:
            #print("\n",i, '\t', wordTag)
            # generate all dependencies related to a verb
            for dep in allVerbDeps:
                if ('discard' not in dep.keys() and 
                    (word in dep['head'] or word in dep['lex'])):
                    pass #print(9, dep)
    """ 
    #print(index, "\t", ss[1:], "\t", root, rootTag, endPunct, "\n")
    #### At this point, our output is sDeps -- a set of dependency sets, one set per sentence

#### Part 3: Turn sDeps information into a table
#### Part 3a: Intermediate table (useful for debugging)
def checkFeatures(complementPos, setDeps, verbComps, headPos):
    for dep in setDeps:
        if dep['headPos'] == complementPos:
            # xsubj is (sometimes?) the binder of a PRO -- not the local subject
            if ('nsubj' in dep['dep'] 
                and 'xsubj' not in dep['dep']
                # and not a long passive's subject
                and 'LB' not in dep['dep']
                # or we are dealing with a pronoun that precedes existence verb 'you'
                or (dep['lexTag'] == 'PN' 
                    and dep['lexPos'] < dep['headPos'] 
                    and dep['headTag'] == 'VE')
                ):
                verbComps[headPos]['embSubject'] = 1
            if (dep['lex'] in modals and
                ('aux:modal' in dep['dep'] 
                or 'advmod' in dep['dep']) 
                and (dep['lexTag'] not in ['DER', 'NN' ])
                ):
                # shoudl be aux:modal (not DER not ACL (会儿))
                # or advmod
                verbComps[headPos]['embModal'] = 1
                verbComps[headPos]['embModalLex'] = dep['lex'] + "" 
            if ((dep['lex'] in aspectPrefix or dep['lex'] in aspectSuffix) and 
                dep['dep'] in ['aux:asp', 'advmod', 'neg']):
                # zhe, le = aux:asp, what about discourse le? (coding not consistent)
                # mei = neg of Verb
                # zai = advmod of verb
                verbComps[headPos]['embAspect'] = 1
            if (
                dep['dep'] == 'discourse'):
                verbComps[headPos]['embDiscourse'] = 1
            if (
                dep['dep'] == 'advmod'):
                verbComps[headPos]['embAdverb'] = 1  
            if (dep['lex'] in neg and 
                dep['dep'] == 'neg'):
                verbComps[headPos]['embNegation'] = 1
            """
            if (dep['lex'].startswith(wh)):
                features['wh'] += 1
            if (dep['dep'] == 'aux:ba'):
                verbComps[headPos]['embBa'] = dep['head']
            if (dep['dep'] == 'auxpass'):
                verbComps[headPos]['embBei'] = dep['head'] + dep['lexTag'] # to distinguish between short and long
            """
            
def initFeatures(sIndex, verb, verbPos, sentence):
    return {'obj': 0,
    'embPreds': [],
    'embPredIsVV': 0,
    'embpred': 0, 
    'embSubject': 0,
    'embModal': 0, 
    'embAspect': 0, 
    'embAdverb': 0, 
    'embDiscourse': 0,
    'embNegation': 0, 
    'sentenceid': sIndex,
    'verb': verb,
    'verbPos': verbPos,
    'utterance': sentence
    }

allFeatures = []

for sIndex, annotation in sDeps.items():
    # Exclude utterances that are just interjections
    if (len(annotation['setDeps']) == 1
        and annotation['setDeps'][0]['headTag'] in ['IJ']
        ):
        pass
    else:
        verbComps = {}
        sentence = annotation['sentence']
        # Create an entry for ROOT
        root = 'ROOT'
        if annotation['prohibitive'] == True:
            root += 'proh'
        if annotation['endPunct'] == '?':
            root += '?'
        verbComps[0] = initFeatures(sIndex, root, 0, sentence)
        
        #verbPositions['root'] = root
        # Create an entry for each verb. Initialize values
        for dep in annotation['setDeps']:
            # Sometimes, modals are classed as verbs. Exclude these
            if (dep['lexTag'][0] in ['V'] and dep['lex'] not in modals):
                verbComps[dep['lexPos']] = initFeatures(sIndex, dep['lex'], dep['lexPos'], sentence)
        
        # At this point we have entries for every verb. We next populate them.
        # We go through every dependency and see what its head is.
        for dep in annotation['setDeps']:
            headPos = dep['headPos']
            # If the head is a verb or root, we ask what kind of dependency is it
            if headPos in verbComps.keys():
                if 'obj' in dep['dep']:
                    verbComps[headPos]['obj'] += 1
                if (dep['dep'] in ['ccomp', 'xcomp', 'root']
                    and 'discard' not in dep.keys()
                    # Ignore dependencies that link 
                    and dep['lexTag'] not in ['PU']):
                    verbComps[headPos]['embpred'] = 1
                    verbComps[headPos]['embPreds'].append(dep['lex'])
                    if dep['lexTag'] in ['VV']:
                        verbComps[headPos]['embPredIsVV'] = 1
                    complementPos = dep['lexPos']
                    checkFeatures(complementPos, annotation['setDeps'], verbComps, headPos)
        allFeatures += verbComps.values()

allF = pd.DataFrame(allFeatures)
"""
allF.to_csv("allFeatures 20200103.csv", encoding='utf-8-sig')
"""

#### Part 3b: Turn the intermediate into a format relevant to the model
### Step 1. Exclude "ROOT?" entries (i.e. questions)
data = allF[allF['verb'] != 'ROOT?']
data['child'] = 'c'

### Helper function to sum up frequency of certain features. Used for debugging / gut checks
def h_sum_features(verb_type, data = data):
    x = data[data.verb == verb_type]
    print([round(prop, 2) for prop in [x.embSubject.mean(), x.embModal.mean(), 
                                       x.embAspect.mean(), x.embDiscourse.mean()]])

""" # Maybe we want to exclude fragment answers like these. Maybe not -- they are relatively few.
data = data[~data['utterance'].isin(['好.', '对.', 
                                    '你.', '我.', '他.', 
                                    '你们.', '我们.', '他们.', 
                                    '谁.', '自己'])]
"""

# CHECK: What are the proportions of overt subjects, etc.?
h_sum_features('ROOT', data)

### Step 3. calculate total number of items, calculate prohibitives n_proh
### 3a. How many non-prohibitives + prohibitives are there?
n_all = data[data['verb'].isin(['ROOT', 'ROOTproh'])].shape[0]

n_decl_ratio = 200/301
### Step 4. Assign a 2:1 ratio for declaratives and imperatives
### a. How many declaratives and imperatives should there be?
n_decl = int(n_all * n_decl_ratio)
n_imp = n_all - n_decl
### b. How many prohibitives are there already?
n_proh = data[data['verb'] == 'ROOTproh'].shape[0]
### c. How many non-prohibitive imperatives should there be?
n_imp_less_proh = n_imp - n_proh

### Step 5. Re-label these entries as DECLARATIVE and IMPERATIVE
### a. label all non-prohibitives as DECLARATIVES
data.verb.replace(to_replace= {'ROOT': 'DECLARATIVE',
                               'ROOTproh': 'IMPERATIVE'}, inplace = True)
h_sum_features('DECLARATIVE', data)
print(data[data['verb'] == 'DECLARATIVE'].shape[0])
h_sum_features('IMPERATIVE', data)
print(data[data['verb'] == 'IMPERATIVE'].shape[0])

if n_imp_less_proh > 0:
    ### b. Take the set of sentences with ROOT and whose heads are Verbs (not adjectives, nouns...)
    ### Randomly select a subset of size n_imp_less_proh
    random_imperative = data[(data['verb'].isin(['DECLARATIVE'])) & 
                             data['embPredIsVV'] == 1].sample(n_imp_less_proh, 
                                                              replace = False, 
                                                              random_state = 0)
    ### d. Label this subset as imperative
    data.loc[random_imperative.index, 'verb'] = 'IMPERATIVE'
    print("DECLARATIVE and IMPERATIVE assigned!")
else:
    print("ERROR!")

h_sum_features('DECLARATIVE', data)
print(data[data['verb'] == 'DECLARATIVE'].shape[0], 
      data[data['verb'] == 'DECLARATIVE'].shape[0] == n_decl)
h_sum_features('IMPERATIVE', data)
print(data[data['verb'] == 'IMPERATIVE'].shape[0],  
      data[data['verb'] == 'IMPERATIVE'].shape[0] == n_imp)

### e. Re-tag subjects, modals, aspect, etc.
### Figures are taken from a hand-coded random sample
data.loc[data['verb'] == 'DECLARATIVE', 'embSubject'] = np.random.binomial(1, .61, size = n_decl)
data.loc[data['verb'] == 'DECLARATIVE', 'embModal'] = np.random.binomial(1, .06, size = n_decl)
data.loc[data['verb'] == 'DECLARATIVE', 'embAspect'] = np.random.binomial(1, .07, size = n_decl)
data.loc[data['verb'] == 'DECLARATIVE', 'embNegation'] = np.random.binomial(1, .17, size = n_decl)
data.loc[data['verb'] == 'DECLARATIVE', 'embDiscourse'] = np.random.binomial(1, .39, size = n_decl)
data.loc[data['verb'] == 'DECLARATIVE', 'embpred'] = 1
data.loc[data['verb'] == 'DECLARATIVE', 'obj'] = 0

data.loc[data['verb'] == 'IMPERATIVE', 'embSubject'] = np.random.binomial(1, .34, size = n_imp)
data.loc[data['verb'] == 'IMPERATIVE', 'embModal'] = np.random.binomial(1, .00, size = n_imp)
data.loc[data['verb'] == 'IMPERATIVE', 'embAspect'] = np.random.binomial(1, .01, size = n_imp)
data.loc[data['verb'] == 'IMPERATIVE', 'embNegation'] = np.random.binomial(1, .04, size = n_imp)
data.loc[data['verb'] == 'IMPERATIVE', 'embDiscourse'] = np.random.binomial(1, .23, size = n_imp)
data.loc[data['verb'] == 'IMPERATIVE', 'embpred'] = 1
data.loc[data['verb'] == 'IMPERATIVE', 'obj'] = 0

### f. Check overall statistics
h_sum_features('DECLARATIVE', data)
print(data[data['verb'] == 'DECLARATIVE'].shape[0], data[data['verb'] == 'DECLARATIVE'].shape[0] == n_decl)
h_sum_features('IMPERATIVE', data)
print(data[data['verb'] == 'IMPERATIVE'].shape[0],  data[data['verb'] == 'IMPERATIVE'].shape[0] == n_imp)

"""
# Convert verbs into numerals, for easier processing (unicode is tricky)
verbIndex = {verbLemma: "v"+str(i) for i, verbLemma in enumerate(data.verb.unique())}
inv_verbIndex = {v: k for k, v in verbIndex.items()}
data.verb.replace(to_replace= verbIndex, inplace = True)
"""


### Step 6. Drop irrelevant columns
data = data.drop(['embModalLex', 'embPreds', 'verbPos', 'embPredIsVV'], axis = 1)

### Step 7. Convert values to TRUE, FALSE
boolean_values_map = {0: 'FALSE', 1: 'TRUE', 2: 'TRUE', 3: 'TRUE', }
for col in data.columns:
    if col not in ['sentenceid', 'utterance', 'verb', 'child']:
        data[col] = data[col].map(boolean_values_map)


# Randomly select 10,000 sentences for each child
children = []
for i in range(22):
    np.random.seed(i)
    random_sentenceid = np.random.choice(data.sentenceid.unique(), 
                                         size = 10000, 
                                         replace = False
                                         )
    
    random_data = data[data['sentenceid'].isin(random_sentenceid)].reset_index(drop = True)
    random_data['child'] = 'c'+ str(i)
    children.append(random_data)
children_data = pd.concat(children)

children_data.to_csv('processedmc22.csv', encoding='utf-8-sig', index=False)

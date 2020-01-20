# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 12:54:12 2019

@author: znhua
"""
import pandas as pd

def splitDep(depStr):
    dep, headlex = depStr[:-2].split("(", 1)
    headi, lexi = headlex.split(", ")
    head, headPos = headi.rsplit("-", 1)
    lex, lexPos = lexi.rsplit("-", 1)
    return {'dep': dep, 'head': head, 'headPos': int(headPos), 
            'lex': lex, 'lexPos': int(lexPos)}
    
wkdir = "C:/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/data/output/"

modals = ["可能", "一定","肯定","或许", "也许",
          "必须", "得",  "肯", "可以", "可", #"要",
          "会", "能够", "能", "应该", "应",
          "将", 
          #"别",
          ]
aspectSuffix = ["了", "过", "着"]
aspectPrefix = ["在", "没有", "没"]
neg = ["不", "没", "没有"]

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
        if deps['dep'] == 'xcomp' and deps['lex'] in ['要', '说', '去', '来','请', '继续']:
            # assign new head
            actualHead = deps['lex']
            actualHeadPos = deps['lexPos']
            actualLex = deps['head']
            actualLexPos = deps['headPos']
            actualLexTag = deps['lexTag']
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
            # if preceding X is the head of the embedded predicate
            # e.g. ?? but just in case
            if (deps['headPos'] < actualHeadPos 
                and deps['lexPos'] == actualLexPos): 
                deps['origLex'] = deps['lex'] # for record-keeping
                deps['lex'] = actualHead
                deps['lexPos'] = actualHeadPos
            # if a punctuation mark that marks 
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
            if (# A-x-AB or AB-x-AB
                (deps['head'] == deps['lex'][0] and deps['headPos'] == deps['lexPos']-2)
                or (deps['head'] == deps['lex'] and deps['headPos'] == deps['lexPos']-2)
                ):
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
    for headLex in headLexs:
        dobjExists = False
        nsubjExists = False
        # go through the set of dependencies
        for deps in setDeps:
            # find instances where the head verb has an object
            # we want to convert this to nsubject
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
            
            """
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
    # At this point we have used xcomp and ccomp to clean up dependencies
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
                # and designate the verb as the root verb
    
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
    

#30 要不要出来 dep (yao, chulai)
# For each sentence, save it and its dependencies in sDeps under its index
sDeps = {}

for index, (wt,td) in enumerate(wttd[:]):
    ss = ""
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
        ss += word
    
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
    sDeps[index]['sentence'] = ss[1:]
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
    #### At this point, our output is sDeps - a set of dependencies for each sentence

"""
# In case we need to re-run this
wttd = list(zip(wt,td))
"""

def initFeatures(dep, sIndex, sentence):
    return {'embeddedBy': dep['head'],
            'embeddedByPos': dep['headPos'],
            'head': dep['lex'],
            'headTag': dep['lexTag'],
            'subject': 0,
            'modal': 0,
            'modalLex':0,
            'aspect': 0,
            'discourse': 0,
            'adverb': 0,
            'negation': 0,
            'sIndex': sIndex,
            'sentence': sentence,
            'ba': 0,
            'bei': 0,
            'obj': 0,
            'verbComp': 0
            }

def checkFeatures(dep, features):
    #print('abc\t', dep2)
    # xsubj is (sometimes?) the binder of a PRO -- not the local subject
    if ('nsubj' in dep['dep'] 
        and 'xsubj' not in dep['dep'] 
        and 'LB' not in dep['dep']
        # or we are dealing with a pronoun that precedes existence verb 'you'
        or (dep['lexTag'] == 'PN' 
            and dep['lexPos'] < dep['headPos'] 
            and dep['headTag'] == 'VE')
        ):
        features['subject'] = 1
    if (dep['lex'] in modals and
        ('aux:modal' in dep['dep'] 
        or 'advmod' in dep['dep']) 
        and (dep['lexTag'] not in ['DER', 'NN' ])
        ):
        # shoudl be aux:modal (not DER not ACL (会儿))
        # or advmod
        features['modal'] = 1
        features['modalLex'] = dep['lex'] + "" 
    if ((dep['lex'] in aspectPrefix or dep['lex'] in aspectSuffix) and 
        dep['dep'] in ['aux:asp', 'advmod', 'neg']):
        # zhe, le = aux:asp, what about discourse le? (coding not consistent)
        # mei = neg of Verb
        # zai = advmod of verb
        features['aspect'] = 1
    if (
        dep['dep'] == 'discourse'):
        features['discourse'] = 1
    if (
        dep['dep'] == 'advmod'):
        features['adverb'] = 1  
    if (dep['lex'] in neg and 
        dep['dep'] == 'neg'):
        features['negation'] = 1
    if (dep['dep'] == 'aux:ba'):
        features['ba'] = dep['head']
    if (dep['dep'] == 'auxpass'):
        features['bei'] = dep['head'] + dep['lexTag'] # to distinguish between short and long
    if ('obj' in dep['dep'] 
       ):
        features['obj'] += 1
    if (dep['dep'] in ['ccomp', 'xcomp'] and 'discard' not in dep.keys()):
        features['verbComp'] = 1

sFeatures = {}
for sIndex, sProperties in sDeps.items():
    rootCompFeats = {}
    sentence = sProperties['sentence']
    for dep in sProperties['setDeps']:
        lex_item = dep['lexPos']
        if dep['dep'] not in ['ccomp', 'xcomp']:
            # these could be subjects, adverbs, etc.
            # a. Main clauses
            # if this lexical item is the root predicate
            if (dep['embeddedBy'] == 'root' and dep['head'] in ['ROOT']
                and dep['lexTag'] not in ['PU', 'IJ']
                ):
                # 'Save' this lexical item in rootDeps
                # i.e., create a set of entries associated with it
                if lex_item not in rootCompFeats.keys():
                    rootCompFeats[lex_item] = initFeatures(dep, sIndex, sentence)
                if sProperties['endPunct'] == "?":
                    rootCompFeats[lex_item]['embeddedBy'] += "?"
                elif sProperties['prohibitive'] == True:
                    rootCompFeats[lex_item]['embeddedBy'] += "Proh"
        # if we are dealing with xcomps and ccomps
        if (dep['dep'] in ['ccomp', 'xcomp']
            # that have been corrected
            and 'discard' not in dep.keys()):
            # b. Complement clauses
            if lex_item not in rootCompFeats.keys():
                rootCompFeats[lex_item] = initFeatures(dep, sIndex, sentence)
    
    # Now that we have created empty entries for each of these "heads"
    # let's run through the dependencies again to complete the entries
    for dep in sProperties['setDeps']:
        headPos = dep['headPos']
        if headPos in rootCompFeats.keys():
            checkFeatures(dep, rootCompFeats[headPos])

    # Once the entries have been updated, "save" them to sFeatures
    # A sentence might have multiple entries (one entry per predicate)
    sFeatures[sIndex] = rootCompFeats

allFeatures = []
for s, headPosFeatures in sFeatures.items():
    for headPos, features in headPosFeatures.items():
        # if we are dealing with just an NP
        # and not a sentence with a nominal predicate, e.g. "John doctor"
        if features['headTag'] == 'NN' and features['subject'] == 0:
            pass
        else:
            # headpos indicates where that lexical item appears in the sentence
            features['headPos'] = headPos
            allFeatures.append(features)

allF = pd.DataFrame(allFeatures)

### For bootstrapping


# list of problems
# many utterances are conjoined, or are particle--clause pairs.
# clauses are inevitably annotated as a "dep" dependent on the particle.
# However, the "dep" dependency is also used more generally
# whenever the parser cannot identify the dependency in question.
"""
import numpy as np
# save output
import pandas as pd
pd.DataFrame(rs).to_csv("allFeatures-random.txt")
allF.to_csv("allFeatures 20200103.csv", encoding='utf-8-sig')

x = np.random.choice(pd.DataFrame(allFeatures)['sIndex'].unique(), size =200)

# save 
wt = list(zip(*wttd))[0]
mcs = []
for i in range(600):
    mc = {}
    i = random.randrange(0, len(wt))
    mc['index'] = i
    mc['s'] = ' '.join(w for w in wt[i])
    preceding = ''
    for s in wt[i-4:i+2]:
        preceding += ' '.join(w for w in s)
    mc['preceding'] = preceding
    mcs.append(mc)
    
pd.DataFrame(mcs).to_csv("random_sample_600main_clauses.txt")

for i in range(4000):
    if "被" in sDeps[i]['sentence']:
        print(sDeps[i])
"""
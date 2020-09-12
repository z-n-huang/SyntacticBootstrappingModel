from nltk.corpus import BracketParseCorpusReader
from nltk.tree import *
import pandas as pd
import os

### Created July 2020
### Modified slightly Sep 2020
### PART ONE
### READ CTB TREES

def returnStringsInd(string, sentSet):
    j = 0
    setStrings = set()
    for sent in sentSet:
        for tag in sent:
            if string in tag[0]:
                #print(tag)
                setStrings.update([tag])
        j = j+1
    return setStrings

def treeAppend(treeAsString,trees,count):
    if len(treeAsString) >0:
        if treeAsString[0] == '(':
            trees.append(ParentedTree.fromstring(treeAsString))
            count = count + 1
        elif treeAsString[0] not in ['<','\n','\r']:
            print(treeAsString)
    treeAsString = ''
    return treeAsString,trees,count
    
def joinLeaves(subtree):
    return ''.join(subtree.leaves())
    
def seqInLabel(seq,label,pos,sent):
    feature = 'na'    
    if seq in label:
        feature = label + '$' + joinLeaves(sent[pos])
    return feature

def daughterNode(motherPos, sent):
    daughterLabelPos = []
    i = 0
    while True:
        daughterPos = motherPos + (i,)
        daughterLabel = 'na'
        #print(daughterPos)
        try:
            daughterLabel = sent[daughterPos].label()
            daughterLeaf = joinLeaves(sent[daughterPos])
            daughterLabelPos.append([daughterLabel, daughterPos, daughterLeaf])
        #IndexError: if no more children; AttributeError: if no label; TypeError: if no daughterPos
        except (IndexError, AttributeError, TypeError):
            break
        #print(daughterLabelPos)        
        i=i+1
    return daughterLabelPos

def seqStrCheck(label, leaf, daughter):
    if label in daughter[0] and leaf == daughter[1]:
        return (daughter[0] + '$' + daughter[1])

corpus_root = r"C:\Users\znhua\bigUSB\biblios\CHILDES\MC\LDC2010T07ptb\LDC2010T07\ctb_7\data\utf-8\bracketed"
file_pattern = r".*/*\.*" #file extensions are abbreviations of genre: nw, nm, bn, bc, wb
filenameList = os.listdir(corpus_root)

#yao4 "fut/want/need"	shuo1 "say"	xiang3 "miss/think/want"	
#zhi1dao4 "know"	jiang3 "say"	xi3huan1 "like"	ai4 "love"	jue2de2 "feel"	
#tao3yan4 "hate"	gan3 "dare"	zhun3bei4 "prepare"	yi3wei2 "(falsely) believe"	
#ming2bai2 "understand"	fa1xian4 "discover"	ren4wei2 "think"	da3suan4 "plan"	
#xi1wang4 "hope"	xiang1xin4 "believe"	dan1xin1 "worry"	huai2yi2 "suspect"
#added: biao3shi4 "to say"
attitudeList = [
                "担心","发现","怀疑",
                "讲","觉得","明白",
                "认为","说",
                "相信","以为","知道",
                
                "讨厌","喜欢","要",
                "爱","敢",
                "打算","准备",
                "想","希望",
                "需要", "须要", "要求", "表示"] 
                
# modals are VV
modalList = ["可能","一定",
             "须", "必须", "得",
             "肯","可","可以","会","能","能够", 
             "应该","应","该",
             "别", "将"]
# negation morphemes are AD
negationList = ["别","不","没","没有","并非","非"]
aspectList = ['没', '没有', '正在', '在']

# '\chtb_0032.nw', '\chtb_4123.bc'
trees = []
fproc = []
fileMetadata = {}
for filename in filenameList:
    #fproc.append(filename)
    count = 0
    #idea: concatenate all lines that are bracketed by XML tags as a single line, 
    #then read that line as a tree
    with open(corpus_root+"\\"+filename, 'r', encoding='utf8') as f:
        treeAsString = ''
        for line in f:
            #Ignore XML tags but...
            if (line[0]=="<"):
                #if we see an XML tag and we have tree brackets in the single line
                #then we should read that line as a tree
                treeAsString,trees,count = treeAppend(treeAsString, trees,count)
            else:
                if (line[0] == "("):
                    #If we see "(" at the start of a line, we have a new tree.
                    #we need to read the existing single line as a tree
                    #And then reset our single line for this new tree                    
                    treeAsString,trees,count = treeAppend(treeAsString, trees,count)
                #add this to the single line
                treeAsString = treeAsString + line
        #Before we close off this file...
        treeAsString,trees,count = treeAppend(treeAsString, trees,count)
    fileMetadata[filename] = count
len(trees) # 51,447 total

def isComplement(subtree):
    isComplement = True
    for flag in ['SBJ' , '-ADV' , '-MNR' , '-CND' , '-TPC' , '-TMP', '-PRD' , '-PRP']:
        if flag in subtree.label():
            isComplement = False
    return isComplement

def notNull(subtree):
    notNull = True
    if len(subtree.leaves()) == 1 and subtree.leaves()[0].startswith('*'):
        notNull = False
    return notNull

def checkClause(subtree, sentProperties):
    verbSeen = False
    clauseSeen = False
    for i, d in enumerate(subtree):
        #print(9, i, clauseSeen, joinLeaves(d))
        try:
            dLabel = d.label()
            dLeaves = d.leaves()
        except AttributeError:
            dLabel = ''
            dLeaves = []
        if clauseSeen == False: # Keep existing entries if we have processed a clause
            checkQmorphology(subtree, sentProperties)
            # if we see anything like a subject
            if 'SBJ' in dLabel:
                sentProperties['subj'] = joinLeaves(d)
                if len(dLeaves) == 1 and dLeaves[0].startswith("*"):
                    sentProperties['hasSubj'] = False
                else:
                    sentProperties['hasSubj'] = True
            if dLabel.startswith('V') and 'SBJ' not in dLabel:
                if dLabel == 'VC':
                    if d.right_sibling() is not None and d.right_sibling().label()[:2] not in ['VP']:
                            verbSeen = True                
                elif dLabel.startswith(('VV', 'VRD')) and dLeaves[0] not in modalList:
                    verbSeen = True
            #print(99, clauseSeen, sentProperties['subj'], dLabel, verbSeen, joinLeaves(d))
                
            if len(dLeaves) == 1:
                dLeaf = dLeaves[0]
                if dLabel.startswith('AD') and dLeaf in negationList:
                    sentProperties['negation'].append(dLeaf)
                if dLabel.startswith(('AD','V')) and dLeaf in modalList:
                    sentProperties['modal'].append(dLeaf)
                if dLabel == 'AS':
                    sentProperties['aspect'].append(dLeaf)
                #pick the instances of mei/meiyou where they negate perfective aspect (POS = 'AD'), 
                #and not uses of NEG exist (POS = 'VE')
                if dLabel.startswith('AD') and dLeaf in aspectList:
                    #print(vpd)
                    sentProperties['aspect'].append(dLeaf)
            elif dLabel.startswith('VNV'):
                #print(88,d.leaves())
                if d.leaves()[1] in negationList:
                    if d.leaves()[0] in modalList:
                        sentProperties['negation'].append(d.leaves()[1])
                        sentProperties['modal'].append(d.leaves()[0])
            # If we have seen a verb
            if verbSeen:
                pass
            else: # if we haven't seen a verb and we haven't seen a clause
                if clauseSeen == False:
                    # but we are looking at a VP, IP, CP, go through this node
                    if dLabel.startswith(('VP', 'IP', 'CP')) and isComplement(d):
                        checkClause(d, sentProperties)
                        #if dLabel.startswith(('VP', 'IP', 'CP')):
                        clauseSeen = True
    
        
def checkQmorphology(d, sentProperties):
    for st in d.subtrees():
        # Wh-words
        if len(st.leaves()) == 1:
            if st.leaves()[0] in ['谁', '什么', '啥', '哪', '怎么', '怎样', '如何', 
                 '干嘛', '干吗', '为何', '为什么', '奈何'
                 ]:
                sentProperties['Qlex'].append(st.leaves()[0])
                sentProperties['Qmorphology'] = 'Q/defWh'
        # A-not-A
        if 'VNV' in st.label():
            sentProperties['Qlex'].append(st.label())
            sentProperties['Qmorphology'] = 'Q/AnotA'
        # Other wh-words
        elif st.label().endswith('WH'):
            sentProperties['Qmorphology'] = 'Q/othWh'

def getBinaryFeats(sentProperties):
    sentProperties['hasNegation'] = len(sentProperties['negation']) > 0
    modalWithoutBie = []
    for mod in sentProperties['modal']:
        if mod == '别':
            sentProperties['Qmorphology'] = 'PROH/bie'
        else:
            modalWithoutBie.append(mod)
    sentProperties['hasModalWithoutBie'] = len(modalWithoutBie) > 0
    sentProperties['clauseSimp'] = str(sentProperties['clause']).startswith(('VP', 'IP', 'CP'))
    sentProperties['hasAspect'] = len(sentProperties['aspect']) > 0
    return sentProperties

def genSentProperties(sentProperties):
    sentProperties['negation'] = []
    sentProperties['modal'] = []
    sentProperties['aspect'] = []
    sentProperties['subj'] = []
    sentProperties['Qmorphology'] = 0
    sentProperties['Qlex'] = []
    sentProperties['clause'] = 0
    sentProperties['hasSubj'] = False
    
    
sentencesFeats = []
for treeIndex, tree in enumerate(trees[51383:51384]):
    mainClause = []
    treeLabel = tree[(0)].label()
    # Don't analyze main clauses that are headlines and fragments
    if 'HLN' in treeLabel or treeLabel.endswith('FRAG'):
        pass
    else:
        mainClauses = []
        # Check to see if a main clause is a set of conjoined clauses
        # i.e. immediately dominates a set of clause-like constituents
        # We exclude VP, because this would incorrectly include VPs inside main clauses
        # Add these constituents to mainClauses
        for i, d in enumerate(tree[(0)]):
            try:
                if d.label().startswith(('IP', 'CP')) and isComplement(d):
                    mainClauses.append(d)
            except:
                print(treeIndex)
        # There are only conjuncts if there are more than two clauses
        # If there is only one 'conjunct', replace mainClauses with only the main clause
        if len(mainClauses) < 2:
            mainClauses = [ tree[(0)] ]
            
        for i, mc in enumerate(mainClauses):
            mcTreeLabel = mc.label()
            att = 'DeclMC'
            if mcTreeLabel.endswith('Q'):
                att = 'Q'
            elif mcTreeLabel.endswith('IMP'):
                att = 'IMP'
            sentProperties = {'treeIndex': treeIndex,
                              'leafIndex': 0,
                              's': joinLeaves(mc),
                              'att': att,
                              'clauseSeen': i > 0 # False if > 0
                              }
            genSentProperties(sentProperties)
            sentProperties['clause'] = mcTreeLabel
            checkClause(mc, sentProperties)
            sentencesFeats.append(sentProperties)
        
    for leafIndex, leaf in enumerate(tree.leaves()):
        for att in attitudeList:
            # if the attitude morpheme is a (proper) substring of the lexical item
            if att == leaf:
                # get the lexical item's position and part of speech
                attLoc = tree.leaf_treeposition(leafIndex)
                attPOS = tree[attLoc[:len(attLoc)-1]].label()
                VP = tree[attLoc[:len(attLoc)-2]]
                # filter for verbs
                
                if attPOS.startswith('V'):
                    verbSeen = False
                    clauseSeen = False
                    NPseen = False
                    NPLabel = ''
                    for d in VP:
                        #print(joinLeaves(d), 999, notNull(d), clauseSeen)
                        if d.leaves() == [leaf]:
                            verbSeen = True
                        if verbSeen:
                            if d.label().startswith(('NP')):
                                NPSeen = True
                                NPLabel = d.label()
                                
                            #print(999, notNull(d), clauseSeen)
                            if (d.label().startswith(('VP', 'IP', 'CP')) and isComplement(d)
                                and notNull(d)
                                # Do we restrict ourselves to the first NP/clausal argument? If yes, uncomment
                                #and clauseSeen == False
                                ):
                                #print(clauseSeen, d.label())
                                sentProperties = {'treeIndex': treeIndex,
                                      'leafIndex': leafIndex,
                                      's': joinLeaves(tree),
                                      'att': leaf
                                      }
                                
                                genSentProperties(sentProperties)
                                sentProperties['np'] = NPLabel
                                sentProperties['clause'] = d.label()
                                sentProperties['clauseSeen'] = clauseSeen
                                clauseSeen = True
                                checkClause(d, sentProperties)
                                sentencesFeats.append(sentProperties)



s = []
for i, sentProperties in enumerate(sentencesFeats):
    if 'clause' in sentProperties.keys():
        sPcleaned = getBinaryFeats(sentProperties)
        s.append(sPcleaned)
pd.DataFrame(s).to_csv("ctb-bootstrap-sep2020-allconjs.txt", index = False)

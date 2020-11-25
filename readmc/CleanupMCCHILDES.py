# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 23:47:16 2019

@author: znhua
from nltk.corpus import BracketParseCorpusReader
from nltk import ParentedTree
import csv

"""
import glob, re, random
import numpy as np, pandas as pd
from nltk.corpus import stopwords
from hanziconv import HanziConv

from collections import Counter
#wkdir = "C:/Users/znhua/bigUSB/corpora/ICE-SIN/ICE-SIN/Spoken/"
wkdir = "C:/Users/znhua/bigUSB/corpora/zhoudinner/ZhouDinner/"
wkdir = "C:/Users/znhua/bigUSB/corpora/MCbootstrappingAll/"
chang = "C:/Users/znhua/bigUSB/biblios/CHILDES/MC/mc5/Chang/Chang"

#allFiles = glob.glob(chang + "*/*.cha")#+

markers = [
"+^", # quick uptakes following an utterance
"+...", # trailoff at end of utterance
"[^c]", # end of clause
"+/.", # interruption by next speaker
"[>]", # overlap follows
"[<]", # overlap precedes
"<", # start of overlap
">", #end of overlap
"++", # finishing someone else's sentence (latching)
"[?]", # best guess of preceding lex item
"[!]", # preceding word is stressed
"[!!]", # preceding word is contrastively stressed
"‡", # satellite markers
"&", # filled pauses,
"=laughs",
"[+ Y]", # not sure what this is?? found in Zhou2
]
repeats = ["[//]", # retrace / restart comes next
"[/]", # repeat comes next 
]
puncts = [".", "！", "?", "!"]
probSFPs = {"咧":'呢', "le":'呢', 
            "伐":"吗", 
            "恩": "嗯", "en": "嗯",
            "啰": "啦", "喏":"啦","嘞":"啦",
            "蛤": "哈", "han": "哈", "hiann": "哈",
            "咧":'呢', 
            "ah":"啊", "嗳": "啊",
            "ㄟ":"啊", "eh":"啊",
            "耶":"啊", 
            "ou":"哦", "ho": "哦",
            }


folders = ["Chang1",
           "Chang2",
           "ChangPNTrad",
           "TCCMTrad",
           "Tong",
           "Zhou1",
           "Zhou2",
           "Zhou3",
           "ZhouAssessment",
           "zhoudinner",
           "ZhouNarratives"
           ]
foldersFull = [wkdir + f + "/" for f in folders]


    
def cleanSentences(line):
    # fix more complex annotation
    line = re.sub("\[=.*?\]", "", line) # removes paralinguisic notation like pointing, laughing
    line = re.sub("\[x.*?\]", "", line) # removes repetition
    line = re.sub("\(\.*?\)", "", line) # removes pauses
    line = re.sub("\\x15.*?\\x15", "", line) # removes icons for playing recordings
    
    # fix corrections
    correction = re.findall("(\s+\S+ )?\[: (\S+)?\] \[\*\]",  line) 
    if len(correction) > 0:
        for (wrong, corrected) in correction:
            line = re.sub("(\s+\S+ )?\[: (\S+)?\] \[\*\]", " "+ corrected, line)
    # fix simpler annotations
    for marker in markers:
        line = line.replace(marker, "")
    for repeat in repeats:
        line = line.replace(repeat, " . ")
    
    # punctuation
    line = line.replace("!", "！").replace(",", " , ").replace("„", ",")
    # strange typo in ZhouAssessment - some kind of search-and-replace error?
    line = line.replace("在1", "在")
    line = line.replace("在2", "在")
    line = line.replace("在3", "在")
    line = line.replace("给1", "给") 
    # if missing a final punctuation mark, add a "."
    if line[-1] not in puncts:
        line += "."
    return line

def replaceChar(line):
    line = line.replace("好不好", "好 不 好").replace("好不 好", "好 不 好").replace("好 不好", "好 不 好")
    line = line.replace("有没有", "有 没 有").replace("有没 有", "有 没 有").replace("有 没有", "有 没 有")
    line = line.replace("行不行", "行 不 行").replace("行不 行", "行 不 行").replace("行 不行", "行 不 行")
    line = line.replace("对不对", "对 不 对").replace("对不 对", "对 不 对").replace("对 不对", "对 不 对")
    line = line.replace("会不会", "会 不 会").replace("会不 会", "会 不 会").replace("会 不会", "会 不 会")
    line = line.replace("是不是", "是 不 是").replace("是不 是", "是 不 是").replace("是 不是", "是 不 是")
    line = line.replace("干吗", "干嘛")
    line = line.replace("不是", "不 是")
    line = line.replace("Chi ", "孩子 ")
    
    for punct in puncts +[","]:
        for probSFP, okSFP in probSFPs.items():
            line = line.replace(probSFP+" "+punct, okSFP+" "+punct)
        # ensure all punctuation get at least one space preceding
        # then change two consecutive spaces to a single space
        line = line.replace(punct, " "+punct).replace("  ", " ")
        
    if "ㄟ" in line:
        line = line.replace("ㄟ", "啊 , ")
    return line

def processFolder(folder):
    allFiles = glob.glob(folder + "**/*.cha", recursive = True) 
    
    filesProcessed = {}
    
    for filename in allFiles:
        file = filename.replace(wkdir, "")
        filesProcessed[file] = []
        with open(filename, "r", encoding = "utf8") as fd:
            raw = fd.readlines()
            
            for line in raw:
                if line.startswith("*"):
                    if "Trad" in filename:
                        filesProcessed[file.replace(wkdir, "")].append(HanziConv.toSimplified(line))
                    else:
                        filesProcessed[file.replace(wkdir, "")].append(line)
                        
    
    filesUtterances = {}
    for filename, lines in filesProcessed.items():
        
        # More pre-processing -- this outputs a cleaned list of dictionaries {speaker: sentences}
        speakerUtterance = []
        
        for line in lines:
            # Remove linebreaks inherited from the original CHAT files
            lineCleaned = line.replace("\n","")
            # Split sentences into speaker, lines
            speaker, line = lineCleaned.split(":\t")
            
            if line.startswith('+"'): 
                # + marks the start of a quote, 
                # try appending it to the previous line, and delete this current line
                if speakerUtterance[-1]['rawSentences'].endswith('+"/.'): # previous line ends with quotation sign
                    speakerUtterance[-1]['rawSentences'] = speakerUtterance[-1]['rawSentences'][:-4] + line[2:]
                    line = "[DEL] "
                else:
                    line = line.replace('+"', "") # just ignore it
            if line.startswith('+,'):
                # +, marks the start of the resumption of an interruption
                if speakerUtterance[-2]['rawSentences'].endswith('+/.'): # if prevPrevSentences was interrupted:
                    speakerUtterance[-2]['rawSentences'] = speakerUtterance[-2]['rawSentences'][:-3] + line[2:]
                    line = "[DEL] "            
                else:
                    line = line.replace('+,', "")
        
            speakerUtterance.append({'speaker': speaker,
                                  'rawSentences': line})
        filesUtterances[filename] = speakerUtterance
    
    # Figure out how many utterances there are in a file
    # Create two lists: one with CHI and one without CHI (child-ambient)
    noUtt = {'withCHI': [], 'woCHI': []}
    for file, utterances in filesUtterances.items():
        noUtt['withCHI'].append(len(utterances))
        uttCountWoCHI = 0
        for utterance in utterances:
            if utterance['speaker'] != '*CHI':
                uttCountWoCHI += 1
        noUtt['woCHI'].append(uttCountWoCHI)
        
    # How many utterances (with CHI and without CHI) are there in a file?
    np.percentile(noUtt['withCHI'], 75), np.percentile(noUtt['withCHI'], 50), np.percentile(noUtt['withCHI'], 25), np.sum(noUtt['withCHI'])
    np.percentile(noUtt['woCHI'], 75), np.percentile(noUtt['woCHI'], 50), np.percentile(noUtt['woCHI'], 25), np.sum(noUtt['woCHI'])
    """ Test sentences for regex
    x = "这 弟弟 [^c] 这 哥哥 [^c] 这 妈妈 [^c] 这 <爸爸> [>] [^c] ."
    y = "<爸爸> [<] 对 ."
    z = "<牠> [/] 牠 躲 在 这 边 [^c] 站 着 [^c] ."
    a = "<在 这> [//] (.) 这 只 跌 倒 了 [=! laughs] [^c] ."
    b = "<不> [/] 不 晓得 [^c] ."
    c = "+^ 这 (.) 狮子 (..) 哥哥 (...) 吗 [^c] ?"
    d = "不 会 飞 [=! laughs] . 不 [x 4] 会 飞 [=! laughs] ."
    e = "然后 牠 [= mommy lion] [=? 小狮子] 就 xxx <去> [/] <去> [/] 去 打仗 了 [^c] ."
    """
    
    fileLineSpeakerCleanOriginal = []
    for file, utterances in filesUtterances.items():
        for lineNo, speakerUtterance in enumerate(utterances):
            # Get child-ambient speech
            # Exclude all utterances by the target child *CHI
            if speakerUtterance['speaker'] != '*CHI':
                splitS = []
                cleanedS = []
                
                originalLine = speakerUtterance['rawSentences'] + ""
                line = cleanSentences(originalLine)
                
                i = 0
                for j, char in enumerate(line): # Go through each character
                    if char in puncts:
                        splitLine = line[i:j+1].replace("  ", " ")
                        if (splitLine.startswith(" \x15") == False
                            and splitLine.startswith("0 ") == False
                            and splitLine != " ."
                            and splitLine not in puncts
                            and "[DEL]" not in splitLine
                            ):
                            splitS.append(splitLine)
                            cleanedS.append(replaceChar(splitLine))
                        i = j+1
                        
                #print(cleanedS)
                for cleanedSentence in cleanedS:
                    cleanedUtterance = cleanedSentence +""
                    fileLineSpeakerCleanOriginal.append(
                        {'file': file,
                         'lineNo': lineNo,
                         'speaker': speakerUtterance['speaker'],
                         'originalLine': originalLine,
                         'cleanedUtterance': cleanedUtterance
                                })

    return fileLineSpeakerCleanOriginal
"""
fileLineSpeakerCleanOriginal = processFolder(foldersFull[0])
pd.DataFrame(fileLineSpeakerCleanOriginal).to_csv('test.txt', index = False)
"""

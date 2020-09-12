# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 23:47:16 2019

@author: znhua
from nltk.corpus import BracketParseCorpusReader
from nltk import ParentedTree
import csv

"""
import glob, re, random
import numpy as np
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
        prevSentences = ""
        prevPrevSentences = ""
        
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
    
    noUtt = {'withCHI': [], 'woCHI': []}
    for file, utterances in filesUtterances.items():
        noUtt['withCHI'].append(len(utterances))
        uttCountWoCHI = 0
        for utterance in utterances:
            if utterance['speaker'] != '*CHI':
                uttCountWoCHI += 1
        noUtt['woCHI'].append(uttCountWoCHI)
        
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
    
    
    for file, utterances in filesUtterances.items():
        for speakerUtterance in utterances:
            speakerUtterance['splitS'] = []
            speakerUtterance['cleanedS'] = []
            line = speakerUtterance['rawSentences'] + ""
            line = cleanSentences(line)
            i = 0
            for j, punct in enumerate(line):
                if punct in puncts:
                    splitLine = line[i:j+1].replace("  ", " ")
                    if (splitLine.startswith(" \x15") == False
                        and splitLine.startswith("0 ") == False
                        and splitLine != " ."
                        and splitLine not in puncts
                        and "[DEL]" not in splitLine
                        ):
                        speakerUtterance['splitS'].append(splitLine)
                        speakerUtterance['cleanedS'].append(replaceChar(splitLine))
                    i = j+1
    
    #splitSpeakers
    # 啊 哦 呀 啦 嗳 恩 哈 哎
    # 呢 嗯 
    # 咧 伐
    
    
    allMainC= []
    allMainCFilename = []
    # check if the processing/cleaning works, and to put all cleaned clauses into allMainC
    for file, utterances in filesUtterances.items():
        allMainC += [file.replace('\\', '-')]
        for utterance in utterances:
            if (utterance['speaker'] != "*CHI"
                ):
                allMainC += utterance['cleanedS']
                allMainCFilename += [file.replace("C:/Users/znhua/bigUSB/corpora/MCbootstrappingAll", "") +", "+ utt for utt in utterance['cleanedS']]
                if (utterance['cleanedS'] != utterance['splitS']
                ):
                    #print("mismatch\t", utterance)
                    pass
            for s in utterance['cleanedS']:
                if '[' in s and '[DEL]' not in s:
                    #print("[] items\t", s)
                    pass
    
    #sample = random.sample(allMainC, 400)
    sample = allMainC   
    
    with open('C:/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/' 
              + 'data/' + folder.replace(wkdir, "").replace("/", "") 
              + '-ntdall.txt', 
              'w', encoding = 'utf') as f:
        for item in sample:
            f.write("%s\n" % item)
            
    for file, utterances in filesUtterances.items():
        for utterance in utterances:
            if (utterance['speaker'] != "*CHI"):
                for s in utterance['cleanedS']:
                    if "[+ Y]" in s:
                        print(file, utterance)
                        
for folder in foldersFull:
    processFolder(folder)
'''
Read Stanford Parser outputs

export CLASSPATH=/mnt/c/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/*:
cd /mnt/c/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17
java -mx2000m edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "wordsAndTags,"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz data/ntd.txt > data/output/wt.txt
java -mx2000m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "typedDependencies"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz  data/ntdall.txt > data/output/tdall.txt
java -mx2000m edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8 \
 -outputFormat "penn"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz \
 data/ntd2.txt > data/output/pn.txt

'''
for f in folders:
    print('java -mx3000m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "typedDependencies"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz  data/' 
          + f +'-ntdall.txt > data/output/' + f + '-tdall.txt')
for f in folders:
    print('java -mx3000m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "wordsAndTags,"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz  data/' 
          + f +'-ntdall.txt > data/output/' + f + '-wtall.txt')


"""
from nltk.parse import CoreNLPParser
from nltk import ParentedTree
# in CMD
EN
cd C:\Users\znhua\Documents\stanford-corenlp-full-2018-10-05
cd C:\Users\znhua\bigUSB\corpora\stanford-corenlp-full-2018-10-05
java -mx1g     -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
-preload tokenize,ssplit,pos,lemma,parse,depparse \
-status_port 9000 -port 9000 -timeout 15000 & 

MC
cd C:\Users\znhua\bigUSB\corpora\stanford-corenlp-full-2018-10-05
java -Xmx1500m -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-chinese.properties -preload tokenize,pos,parse,depparse -status_port 9001  -port 9001 -timeout 15000 &
#
parser = CoreNLPParser(url='http://localhost:9000')
line, = parser.raw_parse('Mary had a little lamb.')

parser = CoreNLPParser('http://localhost:9001')
line = parser.tokenize(u'我家没有电脑。')
list(line)
line = parser.parse(u'我家没有电脑。')

line, = parser.depparse(u'我家没有电脑。')

# this works!#
from nltk.parse.corenlp import CoreNLPDependencyParser
dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')
parse, = dep_parser.raw_parse(
   'The quick brown fox jumps over the lazy dog.'
)

dep_parser = CoreNLPDependencyParser(url='http://localhost:9001')
parse, = dep_parser.raw_parse(
  u'我家没有电脑。'
)

# Generate tagged sentences DONE
# Does it handle SFPs correctly? SORT OF, DONE
# Generate dependency tree DONE
# Check annotation of dependency trees: MOSTLY OK
## how to tell if there are coordinated clauses? NOT WORRYING ABOUT THAT
## how to tell if subordinate clauses? XCOMP (PRO) CCOMP (INTERNAL SUBJECT)

## nice interface but the parsing is terrible
import stanfordnlp
stanfordnlp.download('en')   # This downloads the English models for the neural pipeline
nlp = stanfordnlp.Pipeline() # This sets up a default neural pipeline in English
doc = nlp("Barack Obama was born in Hawaii.  He was elected president in 2008.")
doc.sentences[0].print_dependencies()

stanfordnlp.download('zh')   # This downloads the English models for the neural pipeline
nlp = stanfordnlp.Pipeline(lang= 'zh',
                        processors='tokenize,pos,depparse', ) # This sets up a default neural pipeline in English
doc = nlp("要么 就 吃 饭 要么 就 玩 游戏 .")
doc = nlp(ssRA[4]['procSplitSentences'][0]) 
doc.sentences[0].print_dependencies()

os.environ['STANFORD_PARSER'] = 'C:/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/'
os.environ['STANFORD_MODELS'] = 'C:/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/'

parser = stanford.StanfordParser(model_path="C:/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/englishPCFG.ser.gz")
sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your name?"))
print sentences
"""
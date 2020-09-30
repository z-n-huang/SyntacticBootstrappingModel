# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 16:50:22 2020

@author: znhua
"""
import glob
import stanza
import pandas as pd

"""
stanza.download('zh')   # This downloads the English models for the neural pipeline
stanza.download('zh-hant')   # This downloads the English models for the neural pipeline
"""
nlp = stanza.Pipeline(lang = 'zh', tokenize_pretokenized=True) # This sets up a default neural pipeline in English


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
wh = ["什么", "谁", "哪",  "哪里", "哪儿", "哪边",
      "为什么", "怎么", "怎样", "怎么样", "怎么办",
      "为何", "如何", "多少",
      "干嘛", "干吗", "干什么", "做么", "啥"]

def gen_heads(s):
    # Returns a list of heads and the lexical items that they govern.
    heads = {}
    for t in s.words:
        w_ind = int(t.id)
        """
        deps[w_ind] = {'lex': t.text,
         'pos': t.upos, 
         'dep': t.dependency_relation, 
         'head': t.governor
        }
        """
        if t.head not in heads.keys():
            heads[ t.head ] = []
        
        heads[ t.head ].append({'type': t.deprel,
                                    'ind': w_ind,
                                    'lex': t.text, 
                                    'pos': t.xpos })
    return heads

s_str = "老师 小朋友 说 咦 怎么 张依晨 光 吃 菜 不 吃 饭 的 啦 ?"
s_str = "那 个 爷爷 要 吃 的 ."
s_str = "要 不 要 再 弄 一点 啊 ?"
s_str = "那 你 告诉 姐姐 , 你 为什么 要 说 这 个 词语 呢 ?"
s_str = "你 饭 还 没 动 过 ."
s_str = "菁菁 告诉 她 在 哪 ?"
s_str = "宝宝 啊 , 告诉 妈妈 今天 都 干 什么 了 在 学校 ?"
s_str = "那 你 告诉 妈妈 这 个 小朋友 是 谁 啊 ?"
s_str = "那 你 明白 不 明白 这 个 小朋友 是 谁 啊 ?"
s_str = "那 你 明 不 明白 这 个 小朋友 是 谁 啊 ?"
s_str = "那 你 知道 不 知道 这 个 小朋友 是 谁 啊 ?"
s_str = "那 你 知 不 知道 这 个 小朋友 是 谁 啊 ?"
s_str = "那 你 知道 这 个 小朋友 是 谁 啊 ?"
s_str = "她 说 弟弟 不 能 吃 ."
s_str = "不 知道 柚子 茶 好 不 好 吃 ."
s_str = "那 你 觉得 它 为什么 要 把 这些 东西 放 在 一起 呢 ?"
s_str = "你 把 这 个 拍 下来 给 谁 看 啊 ?"
s_str = "吃 饭 这样 的 , 要 被 老师 骂 了 ！"
s_str = "嗯 , 全 都 被 妈妈 扔 光 了 ."
s_str = "嗯 , 全 都 被 扔 光 了 ."
s_str = "诶 , 都 被 萝卜 吸 掉 了 , 这 个 油 嘛 ！"
s_str = "咦 , 你 看 有 一 粒 米 粒 ！"
s_str = "都 在 看 你 吃 饭 不 吃 饭 , 你 看 ."
s_str = "你 看 王奥 都 吃 完 了 ."
s_str = "你 自己 撕 一 个 , 看看 能 不 能 撕 开 ."
s_str = "我 看 你 吃 一 顿 饭 吃 多 长 时间 ."
s_str = "她 还 没 吃 好 了 呀 ?"
s_str = "妈妈 说 过 吃 饭 不 让 说话 吗 ?"
s_str = "别 看 电视 ！"
s_str = "那 你 以前 睡 过 觉 了 是 不 是 今天 就 不 用 睡觉 了 啊 ?"
s_str = "你 在 干嘛  ?"
s_str = "我 是 谁 的 老婆 啊 ?"



xcomp = ['要', '说', '去', '来', '请', '继续', '用',]

wkdir = r"C:/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/data2/"

allFiles = glob.glob(wkdir + "*.txt", recursive = True) 

for filename in allFiles[9:10]:
    #file = filename.replace(wkdir, "")
    with open(filename, "r", encoding = "utf8") as fd:
        raw = fd.readlines()
print(filename, len(raw))

heads = {}
update_heads = {}
all_deps = []

for s_index, sentence_string in enumerate(raw):
    if s_index%100 == 0:
        print(s_index)
    s_str = sentence_string.replace('\n', '')
    doc = nlp(s_str)
    verb_list = {}
    heads = {}
    update_heads = {}
    embeddings = 0
    for s in doc.sentences:
        heads = gen_heads(s)
    
        # Check for AxA
        # heads = {HEAD_index: [dep1, dep2, ... ], ... } 
        # This adds a "AxA" marker in each dep
        for head_index, deps in heads.items():
            for dep in deps:
                # If there is VV, MD, ... (Cast a wide net)
                if dep['pos'] in ['MD', 'RB', 'VV', 'JJ']:
                    # We look at preceding items
                    if dep['ind'] > 2:                    
                        char_a = dep['lex'][0]
                        lex_minus_2 = s.words[ dep['ind']-1 -2].text[0]
                        lex_minus_1 = s.words[ dep['ind']-1 -1].text
                        
                        #print(999, dep, lex_minus_1, lex_minus_2)
                        type_axa = ''
                        if (lex_minus_2 == char_a):
                            if lex_minus_1 in ['不', '没']:
                                type_axa = 'AnegA'
                            elif (lex_minus_1 in ['一']):
                                type_axa = 'AoneA'
                            
                        if type_axa != '':
                            dep['AxA'] = type_axa                        
    
        def remap(heads):
            # Initialize a dictionary, update_heads
            update_heads = {}
            for head in heads.keys():
                update_heads[head] = []
            
            # Re-map heads, if necessary
            # Sometimes we have HEAD ... DEP when it should be DEP ... HEAD
            # For instance: EAT ... WANT when it should be WANT ... EAT
            # This tracks what heads we need to remap
            embedded_embedding = {}
            embedding_lex = {}
            # How many remaps in total?
            remap_count = 0
            
            for head_ind, deps in heads.items():
                # Go through the dependencies
                for dep in deps:
                    if len(dep.keys()) > 1:
                        xA = False
                        if (dep['pos'] in ['MD', 'VV', 'JJ'] 
                            and (dep['ind']-1 +2) <= len(s.words)):
                            xA = ( s.words[dep['ind']-1 +1].text in ['不', '没', '一'] 
                                and s.words[dep['ind']-1 +2].text[0] == dep['lex'])
                        #print(88, dep)
                        # Make sure that head_ind > 0. head_ind == 0 => ROOT, which is always a head
                        if head_ind > 0 and (
                            # If the lexical item precedes the head and is an xcomp, ccomp, etc.
                            # Lexical items in these relations should come after their heads
                            (
                             dep['ind'] < head_ind and dep['type'] in ['aux', 'xcomp', 'ccomp', 'acl']
                                and dep['lex'] in ['要', '觉得', '知道', '看', '有'] +xcomp
                                and xA == False
                                )
                            # for AxA, especially for verbs, since they embed.
                            # Pass for adjectives in AxA
                            or ('AxA' in dep.keys() and dep['pos'] in ['VV', 'MD'])
                            # Note: parser doesn't handle gaosu very well
                            or (dep['type'] in ['acl'] and dep['lex'] in ['告诉'])
                            # Weird cases of A-not-A
                            ):
                            
                            # Add the entry into heads
                            
                            # Construct a more accurate relation for these dependencies
                            # Call these dependencies Rcomp or Redup (for AxA)
                            comp_type = 'rcomp'
                            if 'AxA' in dep.keys():
                                comp_type = 'redup'
                            
                            deps_for_update = {'type': comp_type,
                               'ind': head_ind,
                               'lex': s.words[head_ind-1].text,
                               'pos': s.words[head_ind-1].xpos
                                }
                            # Add this relation to update_heads
                            update_heads[dep['ind']] = [ deps_for_update ]
                            
                            # If this is a case of AxA, then add a AxA flag
                            # This states that the head has AxA morphology
                            if 'AxA' in dep.keys():
                                update_heads[dep['ind']].append(
                                    {'AxA': dep['AxA'],
                                    })
                            # We track which lexical items have been remapped
                            # Put the syntactically-lower head as the key of the dictionary embedded_embedding
                            embedded_embedding[head_ind] = dep['ind'] #embedded, embedding
                            embedding_lex[dep['ind']] = dep['lex']
                            remap_count += 1
                            
            # Fix AxA coding with root
            if len(heads) > 0:
                #print(99, heads)
                if 'AxA' in heads[0][0].keys():
                    update_heads[ heads[0][0]['ind'] ].append( {'AxA': heads[0][0]['AxA']})
                    
            # At this point, update_heads only has data about the heads that need to be remapped.                    
            # Go through the lexical items again
            for head_ind, deps in heads.items():
                # If the head is a head that has been remapped
                if head_ind in embedded_embedding.keys():
                    for dep in deps:
                        if len(dep.keys()) > 1:
                            # If the dependent precedes the remapped head
                            # it is (most probably) actually a dependent of the new head
                            # Make an exception: discourse particles and punctuation
                            if (dep['ind'] < embedded_embedding[head_ind]
                                or dep['type'] in ['punct', 'discourse']
                            ):
                                update_heads[embedded_embedding[head_ind]].append(dep)
                            # Otherwise, probably a dependent of the old head.
                            elif dep['ind'] > embedded_embedding[head_ind]:
                                update_heads[head_ind].append(dep)
                else:
                    for dep in deps:
                        #print(head_ind, dep['ind'])
                        # If some other head names the remapped head as its dependent
                        # Update the dependency
                        if len(dep.keys()) > 1:
                            if dep['ind'] in embedded_embedding.keys():
                                #print(embedded_embedding[ dep['ind'] ])
                                update_heads[head_ind].append(
                                        {'ind': embedded_embedding[ dep['ind'] ],
                                         'lex': embedding_lex[ embedded_embedding[ dep['ind'] ] ],
                                         'pos': 'VV',
                                         'type': dep['type']})
                            else:
                                update_heads[head_ind].append(dep)
            # In case there are multiple clauses that need remapping, 
            # We need to repeat the process cyclically
            if remap_count > 1:
                update_heads = remap(update_heads)
            return update_heads
        update_heads = remap(heads)
    
        update_heads['sentence'] = [w.text for w in s.words]
        update_heads['pos'] = [w.xpos for w in s.words]
        all_deps.append(update_heads)




def check_deps(update_heads, s_ind = 0, obj = -1, has_clause = True, 
               head_ind = 0, pred_ind = -1):
    
    head_lex = 0
    if head_ind > 0:
        head_lex = update_heads['sentence'][head_ind-1]
    features = {
                'subj': '',
    'has_whAxA': '',
    'neg': '',
    'force': '',
    'modal': '',
    'aspect': '',
    'has_obj': type(obj) == dict,
    'has_clause': has_clause,
    'head': head_lex,
    'pred': pred_ind,
    'clausal_ind': -1,
    's': ' '.join(update_heads['sentence']),
    's_ind': s_ind
    
    }
    obj = -1
    has_clause = False
    
    if pred_ind == -1:
        pred_ind = update_heads[head_ind][0]['ind']
        if features['s'][-1] == '?':
            features['force'] = 'Q' 
    
    features['pred'] = update_heads['sentence'][pred_ind-1]
    if features['pred'] in wh:
        features['has_whAxA'] += 'w'
    if update_heads['pos'][pred_ind-1] == 'VV':
        features['pred'] += 'v'
    
        #features['clausal_ind'] = update_heads['sentence'][pred_ind-1]
    try:
        deps = update_heads[pred_ind]
    except:
        deps = [{'type': 'None', 'lex': 'None', 'pos': 'None', 'ind': -1}]
    
    subj_track = {}
    for dep in deps:
        #if len(dep) > 0:
        #   print(dep)
        if dep == {'AxA': 'AnegA'}:
            features['has_whAxA'] += 'AnegA'
        elif dep == {'AxA': 'AoneA'}:
            features['has_whAxA'] += 'AoneA'
        else:
            if ('nsubj' in dep['type'] 
                or 'csubj' in dep['type'] and dep['lex'] not in [',']):
                features['subj'] = dep['lex']
                if (features['head'] == '告诉' and 'nsubj' in dep['type'] ):
                    subj_track[ dep['ind'] ] = dep
                    if len(subj_track) > 1:
                        obj = subj_track[ min(subj_track.keys()) ]
                        features['has_obj'] = True
            if dep['lex'] in ['不', '没', '没有']:
                features['neg'] = dep['lex']
            # bie
            if dep['lex'] == '别' and (dep['type'] == 'advmod' or dep['type'] == 'RB'):
                features['force'] = 'PROH'
                features['modal'] = dep['lex']
            # Modal
            if (dep['lex'] in modals 
                    and (dep['pos'] in ['MD', 'VV'] 
                        or dep['type'] in ['aux', 'advmod'])):
                features['modal'] = dep['lex']
            # Aspect
            if (dep['lex'] in aspectSuffix and pred_ind < dep['ind']
                    and (dep['pos'] in ['AS']
                        or dep['type'] in ['case:aspect', 'advmod', 'neg'])):
                features['aspect'] = dep['lex']
            if (dep['lex'] in aspectPrefix and dep['ind']< pred_ind):
                features['aspect'] = dep['lex']
            
            # Wh
            if (dep['lex'] in wh):
                features['has_whAxA'] += 'w'
            if (dep['type'] in ['nsubj', 'csubj']):
                if dep['ind'] in update_heads.keys():
                    #print(77, dep)
                    for dep_of_dep in update_heads[ dep['ind'] ]:
                        if len(dep_of_dep.keys()) > 1 and dep_of_dep['lex'] in wh:
                            features['has_whAxA'] += 'w'
            
            if type(obj) == dict:
                if obj['ind'] in update_heads.keys():
                    for dep_of_dep in update_heads[ obj['ind'] ]:
                        if len(dep_of_dep.keys()) > 1 and dep_of_dep['lex'] in wh:
                            features['has_whAxA'] += 'w'
                
            # Complements
            if (dep['type'] in ['rcomp', 'xcomp', 'ccomp', 'obj'] and pred_ind < dep['ind']
                ):
                features['clausal_ind'] = dep['ind']
                if dep['type'] == 'obj':
                    obj = dep
                    #print(obj)
                else:
                    has_clause = True
                
    if features['clausal_ind'] in update_heads.keys():
        #print(features['clausal_ind'])
        pred_entries.append(check_deps(update_heads, s_ind, obj, has_clause, pred_ind, features['clausal_ind']))
    #print(pred, 1, subj, has_whAxA, 3, neg, force,5,  modal, aspect, 7, has_obj)
    return features
    

pred_entries = []
for s_ind, s_dep in enumerate(all_deps):
    pred_entries.append(check_deps(s_dep, s_ind))

filename
pdpe = pd.DataFrame(pred_entries)
pdpe.to_csv('test-stanza-zhounarratives.txt', encoding ='utf8', index = False)


"""
Read Stanford Parser outputs

export CLASSPATH=/mnt/c/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17/*:
cd /mnt/c/Users/znhua/bigUSB/corpora/stanford-parser-full-2018-10-17
java -mx2000m edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "wordsAndTags,"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz data/ntd.txt > data/output/wt.txt
java -mx2000m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "typedDependencies"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz  data/ntdall.txt > data/output/tdall.txt
java -mx2000m edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8 \
 -outputFormat "penn"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz \
 data/ntd2.txt > data/output/pn.txt


for f in folders:
    print('java -mx3000m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "typedDependencies"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz  data/' 
          + f +'-ntdall.txt > data/output/' + f + '-tdall.txt')
for f in folders:
    print('java -mx3000m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8  -outputFormat "wordsAndTags,"  edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz  data/' 
          + f +'-ntdall.txt > data/output/' + f + '-wtall.txt')
"""
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
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 16:50:22 2020

@author: znhua
"""
import glob, random
import stanza
import pandas as pd
import CleanupMCCHILDES as cleanup
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


xcomp = ['要', '说', '去', '来', '请', '继续', '用', '想']

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



heads = {}
update_heads = {}    
def get_deps(sentence_string):
    s_str = sentence_string.replace('\n', '')
    doc = nlp(s_str)
    heads = {}
    update_heads = {}
    
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
                            and dep['lex'] in ['要', '觉得', '知道', '看', '有', '想']
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
                            pass #comp_type = 'redup'
                        
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
                        if s.words[dep['ind']-1].text in ['要', '觉得', '知道', '看', '有'] + xcomp:
                            embedded_embedding[head_ind] = dep['ind'] #embedded, embedding
                            embedding_lex[dep['ind']] = dep['lex']
                        
                        remap_count += 1
        #print(99, heads, embedded_embedding)
        # Fix AxA coding with root
        if len(heads) > 0:
            #print(99, heads)
            if 'AxA' in heads[0][0].keys():
                update_heads[ heads[0][0]['ind'] ].append( {'AxA': heads[0][0]['AxA']})
                
        # At this point, update_heads only has data about the heads that need to be remapped.                    
        # Go through the lexical items again
        for head_ind, deps in heads.items():
            # If the head is a head that has been remapped
            #print(head_ind, deps)
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
        #print(remap_count)
        loop_count = 0
        if remap_count > 1 and loop_count < 0:
            update_heads = remap(update_heads)
            
        return update_heads
    
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
        
        update_heads = remap(heads)
    
        update_heads['sentence'] = [w.text for w in s.words]
        update_heads['pos'] = [w.xpos for w in s.words]
    return update_heads




def check_deps(update_heads, entry = {'cleanedUtterance': 'null'}, 
               s_ind = 0, obj = -1, has_clause = False, 
               head_ind = 0, pred_ind = -1):
    features_list = []
    pred_is_verb = False
    features = entry.copy()
    features.update({
        'subj': '',
        'has_whAxA': '',
        'neg': '',
        'force': '',
        'modal': '',
        'aspect': '',
        'has_obj': type(obj) == dict,
        'has_clause': has_clause,
        'head': 0,
        'pred': pred_ind,
        'clausal_ind': -1,
        #'s': ' '.join(update_heads['sentence']),
    })
    
    #print(features)
    if head_ind == 0:
        # And use punctuation to check for interrogatives, 
        # but only if it's a main clause
        if update_heads['sentence'][-1] == '?':
            features['force'] = 'Q' 
    else:
        # And while at it, if the head is not the root, figure out the main clause
        features['head'] = update_heads['sentence'][head_ind-1]
        

    # Default assumption: there is no dependencies associated with the root/verb
    deps = [{'type': 'None', 'lex': 'None', 'pos': 'None', 'ind': -1}]
    obj = -1 # Reset assumption that there is no object
    if features['head'] in wh:
        features['has_whAxA'] += 'w'
    # pred_ind = position of an embedded predicate or object. Assume there isn't one, i.e. -1
    # If our sentence ends with a "?", it's a question
    
    
    #print("Before.deps", head_ind, features['head'], pred_ind, obj)
    
    # If we know beforehand that there is an embedded verb
    # and that the verb has dependencies, look up its dependencies
    # (Often, there is no embedded verb: no embedded clause for the head verb
    # If so, let it be)
    if pred_ind in update_heads.keys():
        deps = update_heads[pred_ind]
        # What is this predicate? Get the lexical item
    elif head_ind == 0:
        # We don't specify the main verb of the sentence, so we need to locate it
        try:
            # Go to the head, find the first dependency. 
            # Assume this is the predicate / object. Locate its position ('ind')
            first_item = update_heads[head_ind][0]
            pred_ind = first_item['ind']
            #print("Head_index, Pred_info", head_ind, pred_info)
            # 
            if first_item['type'] in ['root', 'rcomp', 'xcomp', 'ccomp']:
                deps = update_heads[pred_ind]
                features['has_clause'] = True
        except:
            # Sometimes we will fail to find an embedded predicate or object.
            # Then leave it as -1
            pred_ind = -1
    #print("After.deps", head_ind, pred_ind, has_clause, deps, obj)
    

    if pred_ind == -1:
        if deps == [{'type': 'None', 'lex': 'None', 'pos': 'None', 'ind': -1}]:
            features['has_clause'] = False
    else:
        pred_is_verb = update_heads['pos'][pred_ind-1].startswith('V')
        features['pred'] = update_heads['sentence'][pred_ind-1]
        if features['pred'] in ['要', '想'] and update_heads['pos'][pred_ind-1] in ['MD']:
            pred_is_verb = True
        # If this lexical item is a wh-word, mark the sentence as bearing a wh-word
        if features['pred'] in wh:
            features['has_whAxA'] += 'w'
        elif features['pred'] in ['不', '没', '没有']:
            features['neg'] = features['pred']
    # So now, we have an embedded predicate and we know what dependencies it has
    subj_track = {} # for gaosu. Stanza handles gaosu weirdly
    pass_subj = False
    # Go through each dependency
    for dep in deps:
        #if len(dep) > 0:
        #   print(dep)
        if dep == {'AxA': 'AnegA'}: #or 'AxA' in dep.keys():
            features['has_whAxA'] += 'AnegA'
        elif dep == {'AxA': 'AoneA'}: #or 'AoneA' in dep.keys():
            features['has_whAxA'] += 'AoneA'
        else:
            if (('nsubj' in dep['type'] or 'csubj' in dep['type'])
                # But sometimes the parser will think that a comma can be a subject!
                and dep['lex'] not in [',', '别']):
                if dep['type'] == 'nsubj:pass':
                    pass_subj = True
                
                if pass_subj == False:
                    features['subj'] = dep['lex']
                # Sometimes the parser will think that gaosu's object is actually a subject!
                if (features['head'] == '告诉' and 'nsubj' in dep['type'] ):
                    # Add all of gaosu's predicate's subjects into a dictionary, subj_track
                    subj_track[ dep['ind'] ] = dep
                    # If gaosu's embedded predicate has two or more subjects,
                    # the first "subject" is probably gaosu's object
                    if len(subj_track) > 1:
                        #obj = subj_track[ min(subj_track.keys()) ] # this gets us the first "subject"
                        features['has_obj'] = True
                        #print(99, features)
                #print("subject", dep, obj)
            # For negation
            if dep['lex'] in ['不', '没', '没有']:
                features['neg'] = dep['lex']
            # bie
            if dep['lex'] == '别' and (dep['type'] in ['advmod','nsubj','RB']):
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
            # Wh inside a NP or clausal subject
            if (dep['type'] in ['nsubj', 'csubj']):
                # If the subject is complex -- has its own dependencies
                if dep['ind'] in update_heads.keys():
                    #print(77, dep)
                    # Go through the subject's dependencies
                    for dep_of_dep in update_heads[ dep['ind'] ]:
                        if len(dep_of_dep.keys()) > 1 and dep_of_dep['lex'] in wh:
                            features['has_whAxA'] += 'w'
            # If we already know that there is an object (e.g. object of gaosu)
            if type(obj) == dict:
                # See if the object is complex enough to have its own dependencies
                #features['has_obj'] = True
                if obj['ind'] in update_heads.keys():
                    for dep_of_dep in update_heads[ obj['ind'] ]:
                        if len(dep_of_dep.keys()) > 1 and dep_of_dep['lex'] in wh:
                            features['has_whAxA'] += 'w'
             
            if (dep['type'] in ['rcomp', 'xcomp', 'ccomp', 'obj'] and 
                pred_ind < dep['ind'] # Check that the head comes before the complement
                ):
                if dep['type'] == 'obj':
                    if dep['lex'] not in [',']:
                        obj = dep
                        has_clause = False
                        features['clausal_ind'] = -1
                        #print(obj, features['clausal_ind'], update_heads.keys())
                else:                    
                    features['has_clause'] = True
                    features['clausal_ind'] = dep['ind']
                    has_clause = True
            
    #if features['clausal_ind'] in update_heads.keys():
        #print(features['clausal_ind'])
    # If we have located a predicate (and have gone through its non-complement dependencies, like its subject and negation)
    #print("Before.analyzing.embedding", pred_ind, update_heads['pos'][pred_ind-1], update_heads['pos'][pred_ind-1].startswith('V'), pred_is_verb, obj, features['clausal_ind'], has_clause)
    if pred_ind != -1 and pred_is_verb:
        
        # Now set the predicate as its own head. See what complements this predicate has
        embedded_pred_features = check_deps(update_heads, entry, s_ind, 
                                            obj, has_clause, 
                                            # Head, predicate
                                            pred_ind, features['clausal_ind'])
        features_list += embedded_pred_features
    #print(pred, 1, subj, has_whAxA, 3, neg, force,5,  modal, aspect, 7, has_obj)
    features_list.append(features)
    return features_list

get_deps('爸爸 拿 , 你 说 .')
check_deps(get_deps('爸爸 拿 , 你 说 .'))
for i, entry in enumerate(cleaned2[:100]):
    if i % 100 == 0:
        print(i)
    deps = get_deps(entry['cleanedUtterance'])
    features_list = check_deps(deps, entry)
features_list 

check_deps(get_deps(cleaned2[-425]['cleanedUtterance']))

"""
all_s = []
for folder in cleanup.foldersFull:
    all_s += cleanup.processFolder(folder)
# all_s ~ 221893. Pick 5000 sentences

# random sample 5000 items without replacement    
samples = {}
for i in range(10):
    random.seed(i)
    samples[i] = random.sample(all_s, 5000)


random.seed(11)
rand_s_index = random.sample(range(len(all_s)), 600)
random_mc = []
for i in rand_s_index:
    random_mc += all_s[i-4:i+2]
pd.DataFrame(random_mc).to_csv("mc600.txt", encoding = "utf-8-sig", index = False)

# TCCM errors 18609, 20253, 32635, 33147, 35430, 35996, 56269, 57032, 57195, 57484
recursion_error = []
pred_entries_x = []

for c, set_entries in samples.items():
    if c == 3:
        for i, entry in enumerate([set_entries[3752], set_entries[4089], set_entries[4280]]):
            if i % 100 == 0:
                print(c, i)
            try:
                deps = get_deps(entry['cleanedUtterance'])
                features_list = check_deps(deps, entry)
                for f in features_list:
                    f['child'] = c
                pred_entries_x += features_list
            except RecursionError:
                recursion_error.append(str(c) + '_' + str(i))
                print(str(c) + '_' + str(i))



folderUse = cleanup.foldersFull[-2]
cleanedSentences = cleanup.processFolder(folderUse)
cleaned2 = cleanedSentences[:300]


for i, entry in enumerate(cleanedSentences[18609:]):
    if i % 100 == 0:
        print(i)
    try:
        deps = get_deps(entry['cleanedUtterance'])
        features_list = check_deps(deps, entry)
        pred_entries_x += features_list
    except RecursionError:
        recursion_error.append(i)
    
pd.DataFrame(pred_entries_x)[[
    "clausal_ind", "cleanedUtterance", "file", "lineNo", 
    "child", "force", "has_whAxA", "head", "has_obj", "has_clause", 
    "subj", "modal", "neg", "aspect", "pred", 
    "originalLine", "speaker"
]].to_csv('mc10all.txt', index = False, encoding = 'utf-8-sig')

pd.DataFrame(pred_entries_x).to_csv("mc10full.txt", index = False, encoding = "utf-8-sig")
pd.DataFrame(random_mc).to_csv("mc.txt", index = False, encoding = "utf-8-sig")
"""
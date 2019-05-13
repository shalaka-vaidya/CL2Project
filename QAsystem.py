from __future__ import unicode_literals
from isc_parser import Parser
import networkx as nx
import nltk
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import re
from indic_transliteration import xsanscript
from indic_transliteration.xsanscript import transliterate
import json
import tree_parsing as tp
import pdb
from isc_parser import Parser

def answerGivenNew(info, storyGrammar, flag):
    if flag==0:
        ep_name=chooseEpisode(storyGrammar, info, "given")
        ans=storyGrammar[ep_name]["new"]
        print(ans)
    else:
        ep_name = chooseEpisode(storyGrammar, info, "new")
        ans = storyGrammar[ep_name]["given"]
        print(ans)


def analyseQuestion(query, storyGrammar):
    words=query.split()
    qType = []
    flag_special=0

    for word in words:
        if word[-4:] == "kara":
            flag_special=1
            newword=word[:-4]
            relevant_words = words[:words.index(word)]
            relevant_words.append(newword)
            given = ' '.join(relevant_words)
            answerGivenNew(given, storyGrammar, 0)

    #if ("kara" in words):
    #    relevant_words=words[:words.index("kara")]
    #    given=' '.join(relevant_words)
    #    answerGivenNew(given,storyGrammar,0)
    if ("bAda" in words):
        flag_special = 1
        relevant_words = words[:words.index("bAda")]
        given = ' '.join(relevant_words)
        answerGivenNew(given, storyGrammar, 0)
    elif ("pahalE" in words):
        flag_special = 1
        relevant_words = words[:words.index("pahalE")]
        new = ' '.join(relevant_words)
        answerGivenNew(new, storyGrammar, 1)
    elif ("kyOM" in words):
        flag_special = 1
        relevant_words = words[:words.index("kyOM")]
        new = ' '.join(relevant_words)
        answerGivenNew(new, storyGrammar, 1)

    else:
        for word in words:
            if word in questionTypes['Karta']:
                qType.append("Karta")
            elif word in questionTypes['Karma']:
                qType.append("Karma")
            elif word in questionTypes['Time']:
                qType.append("time")
            elif word in questionTypes['Loc']:
                qType.append("location")
            elif word in questionTypes['Reciepient']:
                qType.append("rcpt")
            elif word in questionTypes['Adj_noun']:
                qType.append("adj_noun")
                qType.append(words[words.index(word)-1])
            elif word in questionTypes['Intf']:
                qType.append("intf")
                qType.append(words[words.index(word)+1])
            elif word in questionTypes['Kya']:
                qType.append("kya")
            elif word in questionTypes['Kiske']:
                qType.append("kiske")
                qType.append(words[words.index(word) + 1])
            elif word in questionTypes['Kiska']:
                qType.append("kiska")
                qType.append(words[words.index(word) + 1])

    if (flag_special!=1):
        return qType
    else:
        return ["special"]


def k7exception(storyGrammar, ep_name, graph, nodelabel):
    ans=''
    edges_data = graph.edges.data()
    for edges in edges_data:
        if edges[2]['relation'] == 'k7':
            ans= nodelabel[edges[1]]
    return ans

def answerGeneration(storyGrammar, type, ep_name):
    graph, nodeLabels = tp.graphMaking(storyGrammar[ep_name]['parser_output'])
    ans_sent=''
    parser_op=storyGrammar[ep_name]['parser_output']
    if "Karta" in type and 'rcpt' not in type and storyGrammar[ep_name]['karta']!="tbd":

        index=storyGrammar[ep_name]['kartaadj'][0][1][0]
        #print("INDEX", index)
        if index!=-1:
            ans_sent+=parser_op[int(index)-1][1]+' '
        ans_sent+=storyGrammar[ep_name]['karta'][1]
        index = storyGrammar[ep_name]['kartaprep'][0][1][0]
        if index != -1:
            ans_sent +=' '+ parser_op[int(index) - 1][1]

        if ans_sent=='':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "Karma" in type and 'rcpt' not in type and storyGrammar[ep_name]['karmaadj']!='tdb' and storyGrammar[ep_name]['karmaadj']!=[]:
        index=storyGrammar[ep_name]['karmaadj'][0][1][0]
        if index!=-1:
            ans_sent+=parser_op[int(index)-1][1]+' '
        if storyGrammar[ep_name]['karmaadj']!=[]:
            index=storyGrammar[ep_name]['karmaadj'][0][0]
            ans_sent +=parser_op[int(index)-1][1]
        index = storyGrammar[ep_name]['karmaprep'][0][1][0]
        if index != -1:
            ans_sent +=' '+ parser_op[int(index) - 1][1]

        if ans_sent=='':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "time" in type:
        checkK7t=0
        for word in parser_op:
            if word[7]=='k7t':
                checkK7t=1
        if checkK7t==1:
            ans_sent = storyGrammar[ep_name]['time']
        elif checkK7t==0:
            ans_sent=k7exception(storyGrammar,ep_name,graph,nodeLabels)
        elif ans_sent=='' and storyGrammar[ep_name]['time']!='tbd':
            ans_sent = storyGrammar[ep_name]['time']
        if ans_sent == '':
                ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "location" in type:
        checkK7p = 0
        for word in parser_op:
            if word[7] == 'k7p':
                checkK7p = 1

        if checkK7p == 1:
            ans_sent = storyGrammar[ep_name]['location']
        elif checkK7p == 0:
            ans_sent = k7exception(storyGrammar, ep_name, graph, nodeLabels)
        elif ans_sent == '' and storyGrammar[ep_name]['location'] != 'tbd':
            ans_sent = storyGrammar[ep_name]['location']
        if ans_sent=='':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "rcpt" in type:
        mainVerb = tp.templateReturn(tp.main_template, graph['0'])
        if mainVerb[0]!=-1:
            recpient_node = tp.templateReturn(tp.rcp1_template, graph[str(mainVerb[0])])
            if recpient_node[0]==-1:
                recpient_node = tp.templateReturn(tp.rcp2_template, graph[str(mainVerb[0])])
            if recpient_node[0]!=-1:
                word=parser_op[int(recpient_node[0])-1]
                if word[3]!="PRP":
                    ans_sent=word[1]
                else:
                    ans_sent=storyGrammar[ep_name]['karta']
        if ans_sent=='':
            ans_sent=storyGrammar[ep_name]['actual_sentence']

    elif "adj_noun" in type:
        mainNoun = type[type.index("adj_noun")+1]
        nounNode=-1
        for key, value in nodeLabels.items():
            if value == mainNoun:
                nounNode=key
        noun_adj = tp.templateReturn(tp.adj_template, graph[nounNode])
        if (noun_adj[0]!=-1):
            ans_sent=nodeLabels[noun_adj[0]]
        else:
            ans_sent=storyGrammar[ep_name]['actual_sentence']

    elif "intf" in type:
        mainNoun = type[type.index("intf")+1]
        nounNode = -1
        for key, value in nodeLabels.items():
            if value == mainNoun:
                nounNode = key
        noun_intf = tp.templateReturn(tp.intf_template, graph[nounNode])
        noun_adj = tp.templateReturn(tp.adj_template, graph[nounNode])
        if noun_intf[0] != -1:
            ans_sent = nodeLabels[noun_intf[0]]+ " "
        if (noun_adj[0] != -1):
            ans_sent += nodeLabels[noun_adj[0]]
        if ans_sent=='':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kya" in type:
        mainVerb = tp.templateReturn(tp.main_template, graph['0'])
        #print("MV", mainVerb[0])
        if mainVerb[0]!=-1:
            #breakpoint()
            k1s = tp.templateReturn(tp.k1s_template, graph[str(mainVerb[0])])
            if k1s[0] != -1:
                ans_sent=nodeLabels[k1s[0]]
            else:
                pof = tp.templateReturn(tp.pof_template, graph[str(mainVerb[0])])
                if pof[0] != -1:
                    ans_sent = nodeLabels[pof[0]]
                else:
                    k2 = tp.templateReturn(tp.karma_template, graph[str(mainVerb[0])])
                    if k2[0] != -1:
                        ans_sent = nodeLabels[k2[0]]
        if ans_sent == '':
            if storyGrammar[str(int(ep_name)+1)]['given']==storyGrammar[ep_name]['actual_sentence']:
                ans_sent = storyGrammar[str(int(ep_name)+1)]['actual_sentence']
            else:
                ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kiske" in type:
        mainNoun = type[type.index("kiske") + 1]
        nounNode = -1
        for key, value in nodeLabels.items():
            if value == mainNoun:
                nounNode = key
        noun_k7 = tp.templateReturn(tp.k7_template, graph[nounNode])
        noun_r6 = tp.templateReturn(tp.r6_template, graph[nounNode])
        if noun_k7[0] != -1:
            ans_sent = nodeLabels[noun_k7[0]]
        elif (noun_r6[0] != -1):
            ans_sent += nodeLabels[noun_r6[0]]
        if ans_sent == '':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kiska" in type:
        #mainVerb = tp.templateReturn(tp.main_template, graph['0'])
        mainVerb = type[type.index("kiska")+1]
        verbNode = -1
        for key, value in nodeLabels.items():
            if value == mainVerb:
                verbNode = key
        if mainVerb[0] != -1:
            verb_k2 = tp.templateReturn(tp.karma_template, graph[verbNode])
            verb_r6 = tp.templateReturn(tp.r6_template, graph[verbNode])
            verb_k7 = tp.templateReturn(tp.k7_template, graph[verbNode])
            if verb_k2[0] != -1:
                ans_sent=nodeLabels[verb_k2[0]]
            else:
                if verb_k7[0] != -1:
                    ans_sent = nodeLabels[verb_k7[0]]
                if verb_r6[0] != -1:
                    ans_sent=nodeLabels[verb_r6[0]]
        else:
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    print(ans_sent)

def readingFiles(qfname, sgname):
    qfp = open(qfname, "r")
    questions = qfp.readlines()
    with open(sgname) as sgfp:
        storyGrammar=json.load(sgfp)
    #print(storyGrammar)
    for question in questions:
        ep_name=chooseEpisode(storyGrammar, question, "actual_sentence")
        wxques = transliterate(question, xsanscript.DEVANAGARI, xsanscript.HK)
        print(wxques)
        #print("episode", ep_name)
        type = analyseQuestion(wxques, storyGrammar)
        print("type", type)
        if (type != []):
            answerGeneration(storyGrammar, type, ep_name)
        print()

def get_jaccard_sim(str1, str2):
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    Denom = len(a)+len(b)-len(c)
    js = float(len(c))/Denom
    jsN=len(c)
    return js, jsN


def chooseEpisode(storyGrammar, query, matchEntity):
    scList={}
    nscList={}
    highest_match=-1
    ep_name=""
    parser = Parser(lang='hin')
    words = query.split()
    query_tree = parser.parse(words)
    query_graph, query_nodelabels = tp.graphMaking(query_tree)
    query_mv_index=tp.templateReturn(tp.main_template,query_graph['0'])
    #print("EPISODEEEE")
    test_list=[]
    if query_mv_index[0]!=-1:
        query_mv=query_tree[int(query_mv_index[0])-1][1]
    else:
        query_mv=''
    transliterate_query_mv = transliterate(query_mv, xsanscript.DEVANAGARI, xsanscript.HK)
    #print(query)
    for episode,val in storyGrammar.items():
        if (episode!='0'):
            episode_graph, nodeLabels_episode = tp.graphMaking(storyGrammar[episode]['parser_output'])
            episode_mv_index=tp.templateReturn(tp.main_template,episode_graph['0'])
            if episode_mv_index[0] != -1:
                episode_mv = storyGrammar[episode]['parser_output'][int(episode_mv_index[0]) - 1][1]
            else:
                episode_mv = ''
            storySent = val[matchEntity]
            wxques = transliterate(query, xsanscript.DEVANAGARI, xsanscript.HK)
            #print(wxques, storySent)
            sc, nsc = get_jaccard_sim(storySent, wxques)
            scList[episode] = sc
            nscList[episode] = nsc
            ep_info=[sc, transliterate_query_mv, episode_mv]
            test_list.append(ep_info)
            if sc>highest_match:
                highest_match=sc
                ep_name=episode

    #test_list_2=sorted(, key=lambda x: x[0])
    return ep_name

questionTypes1={}
questionTypes1['Karta'] = ["किसने", "किसके", "कौन", "किससे"]
questionTypes1['Karma'] = ["किसको", "किसकी"]
questionTypes1['Time'] = ["कब", "समय", "दिन"]
questionTypes1['Loc'] = ["कहाँ"]
questionTypes1['Reciepient'] = ["किसे"]
questionTypes1['Adj_noun'] = ["कैसा"]
questionTypes1['Intf'] = ["कितना", "कितने"]
questionTypes1['Kya'] = ["क्या"]
questionTypes1['Kiske'] = ["किसके"]
questionTypes1['Kiska'] = ["किसका"]
#questionTypes1['Given'] = [""]

questionTypes={}
for key,value in questionTypes1.items():
    questionTypes[key]=[]
    temp=[]
    for ques in value:
        temp.append(transliterate(ques, xsanscript.DEVANAGARI, xsanscript.HK))
    questionTypes[key]=temp

readingFiles("stories/questions12.txt", "StoryGrammer12.json")
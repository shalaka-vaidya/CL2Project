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

    for word in words:
        if word[-4:] == "kara":
            newword=[:-4]
            relevant_words = words[:words.index(word)]
            relevant_words.append(newword)
            given = ' '.join(relevant_words)
            answerGivenNew(given, storyGrammar, 0)

    if ("kara" in words):
        relevant_words=words[:words.index("kara")]
        given=' '.join(relevant_words)
        answerGivenNew(given,storyGrammar,0)
    if ("bAda" in words):
        relevant_words = words[:words.index("bAda")]
        given = ' '.join(relevant_words)
        answerGivenNew(given, storyGrammar, 0)
    if ("pahalE" in words):
        relevant_words = words[:words.index("pahalE")]
        new = ' '.join(relevant_words)
        answerGivenNew(new, storyGrammar, 1)
    if ("kyOM" in words):
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
        return qType


def k7exception(storyGrammar, ep_name, graph, nodelabel):
    ans=''
    edges_data = graph.edges.data()
    for edges in edges_data:
        if edge[2]['relation'] == 'k7':
            ans= nodelabel[edges[1]]
    return ans

def answerGeneration(storyGrammar, type, ep_name):
    graph, nodeLabels = tp.graphMaking(storyGrammar[ep_name]['parser_output'])
    ans_sent=''
    parser_op=storyGrammar[ep_name]['parser_output']
    if "Karta" in type and 'rcpt' not in type:
        index=storyGrammar[ep_name]['kartaadj'][0][1][0]
        if index!=-1:
            ans_sent+=parser_op[int(index)-1][1]+' '
        ans_sent+=storyGrammar[ep_name]['karta'][1]
        index = storyGrammar[ep_name]['kartaprep'][0][1][0]
        if index != -1:
            ans_sent +=' '+ parser_op[int(index) - 1][1]

    elif "Karma" in type and 'rcpt' not in type:
        index=storyGrammar[ep_name]['karmaadj'][0][1][0]
        if index!=-1:
            ans_sent+=parser_op[int(index)-1][1]+' '
        if storyGrammar[ep_name]['karmaadj']!=[]:
            index=storyGrammar[ep_name]['karmaadj'][0][0]
            ans_sent +=parser_op[int(index)-1][1]
        index = storyGrammar[ep_name]['karmaprep'][0][1][0]
        if index != -1:
            ans_sent +=' '+ parser_op[int(index) - 1][1]

    elif "Time" in type:
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
        else:
            ans_sent=storyGrammar[ep_name]['actual_sentence']

    elif "Loc" in type:
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
        else:
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "rcpt" in type:
        mainVerb = tp.templateReturn(tp.main_template, graph[0])
        if mainVerb[0]!=-1:
            recpient_node = tp.templateReturn(tp.rcp1_template, graph[mainVerb[0]])
            if recpient_node[0]==-1:
                recpient_node = tp.templateReturn(tp.rcp2_template, graph[mainVerb[0]])
            if recpient_node[0]!=-1:
                word=parser_op[int(recpient_node[0])-1]
                if word[3]!="PRP":
                    ans_sent=word[1]
                else:
                    ans_sent=storyGrammar[ep_name]['karta']
        else:
            ans_sent=storyGrammar[ep_name]['actual_sentence']

    elif "adj_noun" in type:
        mainNoun = type[type.index("adj_noun")+1]
        nounNode=-1
        for key, value in nodeLabels.items():
            if value == mainNoun:
                nounNode=key
        noun_adj = tp.templateReturn(tp.adj_template, graph[int(nounNode)])
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
        noun_intf = tp.templateReturn(tp.intf_template, graph[int(nounNode)])
        noun_adj = tp.templateReturn(tp.adj_template, graph[int(nounNode)])
        if noun_intf[0] != -1:
            ans_sent = nodeLabels[noun_intf[0]]+ " "
        if (noun_adj[0] != -1):
            ans_sent += nodeLabels[noun_adj[0]]
        elif ans_sent=='':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kya" in type:
        mainVerb = tp.templateReturn(tp.main_template, graph[0])
        if mainVerb[0]!=-1:
            k1s = tp.templateReturn(tp.k1s_template, mainVerb[0])
            if k1s[0] != -1:
                ans_sent=nodeLabels[k1s[0]]
            else:
                pof = tp.templateReturn(tp.pof_template, mainVerb[0])
                if pof[0] != -1:
                    ans_sent = nodeLabels[pof[0]]
                else:
                    k2 = tp.templateReturn(tp.karma_template, mainVerb[0])
                    if k2[0] != -1:
                        ans_sent = nodeLabels[k2[0]]
        if ans_sent == '':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kiske" in type:
        mainNoun = type[type.index("intf") + 1]
        nounNode = -1
        for key, value in nodeLabels.items():
            if value == mainNoun:
                nounNode = key
        noun_k7 = tp.templateReturn(tp.k7_template, graph[int(nounNode)])
        noun_r6 = tp.templateReturn(tp.r6_template, graph[int(nounNode)])
        if noun_k7[0] != -1:
            ans_sent = nodeLabels[noun_k7[0]]
        elif (noun_r6[0] != -1):
            ans_sent += nodeLabels[noun_r6[0]]
        elif ans_sent == '':
            ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kiska" in type:
        mainVerb = tp.templateReturn(tp.main_template, graph[0])
        if mainVerb[0] != -1:
            verb_k2 = tp.templateReturn(tp.karma_template, graph[int(mainVerb[0])])
            verb_r6 = tp.templateReturn(tp.r6_template, graph[int(mainVerb[0])])
            verb_k7 = tp.templateReturn(tp.k7_template, graph[int(mainVerb[0])])
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
    print(storyGrammar)
    for question in questions:
        ep_name=chooseEpisode(storyGrammar, question, "actual_sentence")
        type = analyseQuestion(question, storyGrammar)
        answerGeneration(storyGrammar, type, ep_name)


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
    for episode,val in storyGrammar.items():
        storySent = val[matchEntity]
        wxques = transliterate(query, xsanscript.DEVANAGARI, xsanscript.HK)
        sc, nsc = get_jaccard_sim(storySent, wxques)
        scList[episode] = sc
        nscList[episode] = nsc
        if sc>highest_match:
            highest_match=sc
            ep_name=episode
    return ep_name

questionTypes={}
questionTypes['Karta'] = ["किसने", "किसके", "कौन", "किससे"]
questionTypes['Karma'] = ["किसको", "किसकी"]
questionTypes['Time'] = ["कब", "समय", "दिन"]
questionTypes['Loc'] = ["कहाँ"]
questionTypes['Reciepient'] = ["किसे"]
questionTypes['Adj_noun'] = ["कैसा"]
questionTypes['Intf'] = ["कितना", "कितने"]
questionTypes['Kya'] = ["क्या"]
questionTypes['Kiske'] = ["किसके"]
questionTypes['Kiska'] = ["किसका"]
questionTypes['Given'] = [""]

readingFiles("stories/sampleq", "StoryGrammer.json")
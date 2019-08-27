from __future__ import unicode_literals
from isc_parser import Parser
from isc_tokenizer import Tokenizer
from isc_tagger import Tagger
import networkx as nx
import nltk
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import re
from indic_transliteration import xsanscript
from indic_transliteration.xsanscript import transliterate
import verbnounreol
import json
import tree_parsing as tp
import pdb
from isc_parser import Parser
import verbnounreol

QuestionDic = {}


# quesComparision = open("stories/comparision1.txt", "w")

def answerGivenNew(info, storyGrammar, flag, ansfname):
    jaccardcomp = verbnounreol.mainFunction(info, transliterate(info, xsanscript.DEVANAGARI, xsanscript.HK))
    if flag == 0:
        #print(info)
        #made changes
        ep_name = chooseEpisode(storyGrammar, info, "given",jaccardcomp, ansfname)
        # print("Episode chosen is ",ep_name)
        ans = storyGrammar[ep_name]["new"]
        print("answer in given ",ans)
        ansfname.write(ans+"\n")
    else:
        #made changes
        ep_name = chooseEpisode(storyGrammar, info, "new", jaccardcomp, ansfname)
        print("Episode chosen is ",ep_name)
        ans = storyGrammar[ep_name]["given"]

        print("answer in new ",ans)
        ansfname.write(ans + "\n")


def analyseQuestion(query, storyGrammar, ansfname):
    ansfname.write("query "+ query)
    words = query.split()
    qType = []
    flag_special = 0
    flag_given = 0
    match_entity=None
    info=None
    givenOrNew=-1

    for word in words:
        if word[-4:] == "kara":
            flag_given = 1
            flag_special = 1
            newword = word[:-4]
            relevant_words = words[:words.index(word)]
            relevant_words.append(newword)
            given = ' '.join(relevant_words)
            match_entity="given"
            #ansfname.write("MUAHAHA"+word)
            info=given
            givenOrNew=0
            #answerGivenNew(given, storyGrammar, 0, ansfname)

    if ("bAda" in words and flag_given == 0):
        flag_special = 1
        flag_given = 1
        relevant_words = words[:words.index("bAda")]
        given = ' '.join(relevant_words)
        match_entity = "given"
        ansfname.write("MUAHAHA" + word)
        info = given
        givenOrNew = 0
        #answerGivenNew(given, storyGrammar, 0, ansfname)
    elif ("pahalE" in words and flag_given == 0):
        flag_special = 1
        flag_given = 1
        relevant_words = words[:words.index("pahalE")]
        new = ' '.join(relevant_words)
        match_entity = "new"
        ansfname.write("MUAHAHA" + word)
        info = new
        givenOrNew = 1
        #answerGivenNew(new, storyGrammar, 1, ansfname)
    elif ("kyOM" in words and flag_given == 0):
        flag_special = 1
        flag_given = 1
        relevant_words = words[:words.index("kyOM")]
        new = ' '.join(relevant_words)
        match_entity = "new"
        ansfname.write("MUAHAHA" + word)
        info = new
        givenOrNew = 1
        #answerGivenNew(new, storyGrammar, 1, ansfname)

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
                qType.append(words[words.index(word) - 1])
            elif word in questionTypes['Intf']:
                qType.append("intf")
                qType.append(words[words.index(word) + 1])
            elif word in questionTypes['Kya']:
                qType.append("kya")
            elif word in questionTypes['Kiske']:
                qType.append("kiske")
                qType.append(words[words.index(word) + 1])
            elif word in questionTypes['Kiska']:
                qType.append("kiska")
                qType.append(words[words.index(word) + 1])


    print("HAHAHA       ", qType)
    print("WOrds        ", words)

    if (flag_given == 1 and "kya" in qType and "kara" in words):
        return [qType, "nounVerbSentence"]
    elif (flag_special != 1):
        return [qType, "nounVerbSentence"]
    elif(flag_given):
        return ["special", match_entity, info, givenOrNew]


def k7exception(storyGrammar, ep_name, graph, nodelabel):
    ans = ''
    edges_data = graph.edges.data()
    for edges in edges_data:
        if edges[2]['relation'] == 'k7':
            ans = nodelabel[edges[1]]
    return ans


def answerGeneration(storyGrammar, type, ep_name, ansfname):
    # print("In answer Generation", ep_name)
    # print("In answer Generation", storyGrammar[ep_name]['actual_sentence'])
    graph, nodeLabels = tp.graphMaking(storyGrammar[ep_name]['parser_output'])
    ans_sent = ''
    parser_op = storyGrammar[ep_name]['parser_output']
    if "Karta" in type and 'rcpt' not in type and storyGrammar[ep_name]['karta'] != "tbd":
        index = storyGrammar[ep_name]['kartaadj'][0][1][0]
        if index != -1:
            ans_sent += parser_op[int(index) - 1][1] + ' '
            ans_sent += storyGrammar[ep_name]['karta'][1]
        index = storyGrammar[ep_name]['kartaprep'][0][1][0]
        if index != -1:
            ans_sent += ' ' + parser_op[int(index) - 1][1]
        if ans_sent == '' or ans_sent == "tbd":
            #ans_sent = storyGrammar[ep_name]['resolvedsent']
            ans_sent = storyGrammar[ep_name]['actual_sentence']
    elif "Karma" in type and 'rcpt' not in type and storyGrammar[ep_name]['karmaadj'] != 'tdb' and \
            storyGrammar[ep_name]['karmaadj'] != []:
        index = storyGrammar[ep_name]['karmaadj'][0][1][0]
        if index != -1:
            ans_sent += parser_op[int(index) - 1][1] + ' '
        if storyGrammar[ep_name]['karmaadj'] != []:
            index = storyGrammar[ep_name]['karmaadj'][0][0]
            ans_sent += parser_op[int(index) - 1][1]
        index = storyGrammar[ep_name]['karmaprep'][0][1][0]
        if index != -1:
            ans_sent += ' ' + parser_op[int(index) - 1][1]

        if ans_sent == '' or ans_sent == "tbd":
            ans_sent = storyGrammar[ep_name]['resolvedsent']
            #ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "time" in type:
        checkK7t = 0
        for word in parser_op:
            if word[7] == 'k7t':
                checkK7t = 1
        if checkK7t == 1:
            ans_sent = storyGrammar[ep_name]['time']
        elif checkK7t == 0:
            ans_sent = k7exception(storyGrammar, ep_name, graph, nodeLabels)
        elif ans_sent == '' and storyGrammar[ep_name]['time'] != 'tbd':
            ans_sent = storyGrammar[ep_name]['time']
        if ans_sent == '' or ans_sent == "tbd":
            ans_sent = storyGrammar[ep_name]['resolvedsent']
            #ans_sent = storyGrammar[ep_name]['actual_sentence']

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
        if ans_sent == '' or ans_sent == "tbd":
            ans_sent = storyGrammar[ep_name]['resolvedsent']
            #ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "rcpt" in type:
        mainVerb = tp.templateReturn(tp.main_template, graph['0'])
        if mainVerb[0] != -1:
            recpient_node = tp.templateReturn(tp.rcp1_template, graph[str(mainVerb[0])])
            if recpient_node[0] == -1:
                recpient_node = tp.templateReturn(tp.rcp2_template, graph[str(mainVerb[0])])
            if recpient_node[0] != -1:
                word = parser_op[int(recpient_node[0]) - 1]
                if word[3] != "PRP":
                    ans_sent = word[1]
                else:
                    ans_sent = storyGrammar[ep_name]['karta']
        if ans_sent == '' or ans_sent == "tbd":
            ans_sent = storyGrammar[ep_name]['resolvedsent']
            #ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "adj_noun" in type:
        mainNoun = type[type.index("adj_noun") + 1]
        nounNode = -1
        for key, value in nodeLabels.items():
            if value == mainNoun:
                nounNode = key
        noun_adj = tp.templateReturn(tp.adj_template, graph[nounNode])
        if (noun_adj[0] != -1):
            ans_sent = nodeLabels[noun_adj[0]]
        else:
            if ans_sent == '' or ans_sent == "tbd":
                ans_sent = storyGrammar[ep_name]['resolvedsent']
                #ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "intf" in type:
        mainNoun = type[type.index("intf") + 1]
        #print("MAIN "+mainNoun)
        nounNode = -1
        noun_intf = [-1]
        noun_adj = [-1]
        for key, value in nodeLabels.items():
            if value == mainNoun:
                nounNode = key
        #print("nodeKey", nounNode)
        if nounNode!=-1:
            noun_intf = tp.templateReturn(tp.intf_template, graph[nounNode])
            noun_adj = tp.templateReturn(tp.adj_template, graph[nounNode])
        if noun_intf[0] != -1:
            ans_sent = nodeLabels[noun_intf[0]] + " "
        if (noun_adj[0] != -1):
            ans_sent += nodeLabels[noun_adj[0]]
        if ans_sent == '' or ans_sent == "tbd":
            ans_sent = storyGrammar[ep_name]['resolvedsent']
            #ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kya" in type:
        mainVerb = tp.templateReturn(tp.main_template, graph['0'])
        # print("MV", mainVerb[0])
        if mainVerb[0] != -1:
            k1s = tp.templateReturn(tp.k1s_template, graph[str(mainVerb[0])])
            if k1s[0] != -1:
                ans_sent = nodeLabels[k1s[0]]
                print("k1s")
            else:
                pof = tp.templateReturn(tp.pof_template, graph[str(mainVerb[0])])
                if pof[0] != -1:
                    ans_sent = nodeLabels[pof[0]]
                    print("pof")
                else:
                    k2 = tp.templateReturn(tp.karma_template, graph[str(mainVerb[0])])
                    if k2[0] != -1:
                        ans_sent = nodeLabels[k2[0]]
                        print("third")
        print("answerrr     ", ans_sent)
        """checkkkkkkkkkkkkkkk"""
        if ans_sent == '' or ans_sent == "tbd":
            if storyGrammar[str(int(ep_name) + 1)]['given'] != "tbd":
                #if storyGrammar[str(int(ep_name) + 1)]['given'] == storyGrammar[ep_name]['actual_sentence']:
                #print(ep_name)
                ans_sent = storyGrammar[str(int(ep_name) + 1)]['resolvedsent']
                #ans_sent = storyGrammar[str(int(ep_name) + 1)]['actual_sentence']
            else:
                ans_sent = storyGrammar[ep_name]['resolvedsent']
                #ans_sent = storyGrammar[ep_name]['actual_sentence']

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
        if ans_sent == '' or ans_sent == "tbd":
            ans_sent = storyGrammar[ep_name]['resolvedsent']
            #ans_sent = storyGrammar[ep_name]['actual_sentence']

    elif "kiska" in type:
        # mainVerb = tp.templateReturn(tp.main_template, graph['0'])
        mainVerb = type[type.index("kiska") + 1]
        verbNode = -1
        for key, value in nodeLabels.items():
            if value == mainVerb:
                verbNode = key
        if mainVerb[0] != -1:
            verb_k2 = tp.templateReturn(tp.karma_template, graph[verbNode])
            verb_r6 = tp.templateReturn(tp.r6_template, graph[verbNode])
            verb_k7 = tp.templateReturn(tp.k7_template, graph[verbNode])
            if verb_k2[0] != -1:
                ans_sent = nodeLabels[verb_k2[0]]
            else:
                if verb_k7[0] != -1:
                    ans_sent = nodeLabels[verb_k7[0]]
                if verb_r6[0] != -1:
                    ans_sent = nodeLabels[verb_r6[0]]
        if ans_sent == '' or ans_sent == "tbd":
            ans_sent = storyGrammar[ep_name]['resolvedsent']
            #ans_sent = storyGrammar[ep_name]['actual_sentence']
    print("Answer is ", ans_sent)
    ansfname.write(ans_sent+"\n")



def readingFiles(qfname, sgname, ansfname):
    QuesCompare = []
    qfp = open(qfname, "r")
    questions = qfp.readlines()
    with open(sgname) as sgfp:
        storyGrammar = json.load(sgfp)

    for question in questions:
        wxquestion = transliterate(question, xsanscript.DEVANAGARI, xsanscript.HK)
        wxques=verbnounreol.mainFunction(question,wxquestion)
        ansfname.write(wxquestion+"\n")
        type = analyseQuestion(wxques, storyGrammar,ansfname)
        #type = analyseQuestion(wxquestion, storyGrammar,ansfname)
        ansfname.write("TYPE:" + str(type))
        # print("type", type)
        if (type != []):
            if (type[0]!="special"):
                jaccardcomp = verbnounreol.mainFunction(question, wxquestion)
                #made changes
                ep_name_new = chooseEpisode(storyGrammar, wxques, "nounVerbSentence", jaccardcomp, ansfname)
                #ep_name_new = chooseEpisode(storyGrammar, wxquestion, 'actual_sentence', wxquestion,ansfname)
                #ep_name_new = chooseEpisode(storyGrammar, question, 'resolvedsent', wxquestion)
                answerGeneration(storyGrammar, type[0], ep_name_new, ansfname)
            else:
                answerGivenNew(type[2], storyGrammar, type[3], ansfname)
        print("---------------")
        ansfname.write("---------------\n\n\n")
    # print()


# return(QuesCompare)
def get_pos_tag(sent):
    SentTag = {}
    sent_trans = transliterate(sent, xsanscript.HK, xsanscript.DEVANAGARI)
    # print("Received Sent is ", sent_trans)
    tk = Tokenizer(lang='hin')
    tagger = Tagger(lang='hin')
    sequence = tk.tokenize(sent_trans)
    # print("sequence is ", sequence)
    tagged = tagger.tag(sequence)
    # print("Tagged", tagged)
    for match in tagged:
        SentTag[transliterate(match[0], xsanscript.DEVANAGARI, xsanscript.HK)] = match[1]
    # print(SentTag)
    return SentTag


def get_jaccard_sim(str1, str2):
    TagC = []
    SimiNum = 0
    NounTags = ["NNP", "NNS", "NN"]
    VerbTags = ["VM"]
    VAuxTags = ["VAUX"]
    AdTags = ["JJ", "RB"]

    a = set(str1.split())
    TagA = get_pos_tag(str1)
    # print("TagA type", type(TagA))
    b = set(str2.split())
    TagB = get_pos_tag(str2)
    c = a.intersection(b)
    # print("Int",c)
    for word in c:
        # print("Intersection Word",word)

        TagC.append(TagA[word])
    for tags in TagC:
        if (tags in NounTags):
            SimiNum = SimiNum + 3
        elif (tags in VerbTags):
            SimiNum = SimiNum + 4
        elif (tags in AdTags):
            SimiNum = SimiNum + 5
        elif (tags in VAuxTags):
            SimiNum = SimiNum + 2
        else:
            SimiNum = SimiNum + 1
    # print("New JS is ",SimiNum)
    # quesComparision.write(str(SimiNum))
    # quesComparision.write("\n")
    Denom = len(a) + len(b) - len(c)
    js = float(SimiNum) / Denom
    return js, SimiNum


def old_get_jaccard_sim(str1, str2):
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    Denom = len(a) + len(b) - len(c)
    jsN = len(c)
    js = float(jsN) / Denom
    # print("Old JS is ",jsN)
    # print("\n-------------------------------\n")
    # quesComparision.write(str(jsN))
    # quesComparision.write("\n")
    # quesComparision.write("-----------")
    # quesComparision.write("\n")
    #print("OLDDDDD", js, jsN )
    return js, jsN


def chooseEpisode(storyGrammar, query, matchEntity, jaccard_comparison, ansfile):
    #print("matchEntity", matchEntity)
    scList = {}
    nscList = {}
    ep_name_new = ""
    ep_name_old = ""
    highest_match_nsc = -1
    highest_match_sc = -1
    highest_match_old = -1

    parser = Parser(lang='hin')
    words = query.split()
    query_tree = parser.parse(words)
    query_graph, query_nodelabels = tp.graphMaking(query_tree)
    query_mv_index = tp.templateReturn(tp.main_template, query_graph['0'])
    test_list_new = []
    test_list_old = []
    if query_mv_index[0] != -1:
        query_mv = query_tree[int(query_mv_index[0]) - 1][1]
    else:
        query_mv = ''
    transliterate_query_mv = transliterate(query_mv, xsanscript.DEVANAGARI, xsanscript.HK)
    # print("Query is ",transliterate(query, xsanscript.DEVANAGARI, xsanscript.HK))
    # quesComparision.write(query)
    for episode, val in storyGrammar.items():
        if (episode != '0'):
            transliterate_query_mv= (val["actual_sentence"])
            episode_graph, nodeLabels_episode = tp.graphMaking(storyGrammar[episode]['parser_output'])
            episode_mv_index = tp.templateReturn(tp.main_template, episode_graph['0'])
            if episode_mv_index[0] != -1:
                episode_mv = storyGrammar[episode]['parser_output'][int(episode_mv_index[0]) - 1][1]
            else:
                episode_mv = ''

            if matchEntity=="given":
                if val["given"] != "tbd":
                    storySent = storyGrammar[str(int(episode)-1)]['nounVerbSentence']
                    #storySent = storyGrammar[str(int(episode)-1)]['actual_sentence']
                else:
                    storySent="tbd"
            else:
                storySent = val['nounVerbSentence']
                #print(episode, storySent)
                #storySent = val['actual_sentence']
            #storySent = val[matchEntity]

            old_story_sent = val[matchEntity]
            wxques = transliterate(jaccard_comparison, xsanscript.DEVANAGARI, xsanscript.HK)
            # print("Here",wxques, storySent)
            # print("Story Sentence is ", storySent)
            # print("Question", wxques)
            # print()
            # quesComparision.write(storySent)
            # #quesComparision.write("\n")
            ansfile.write("\n\nJaccard comparison between"+ storySent + ' and '+ wxques+'\n\n')
            new_sc, new_nsc = get_jaccard_sim(storySent, wxques)
            #print("imp",storySent, new_nsc)
            scList[episode] = new_sc
            nscList[episode] = new_nsc
            ansfile.write("\njaccardscore:"+ str(new_nsc)+"\n")
            ep_info = [episode, new_nsc, transliterate_query_mv, episode_mv]
            test_list_new.append(ep_info)
            if new_nsc > highest_match_nsc:
                highest_match_nsc = new_nsc
                highest_match_sc = new_sc
                ep_name_new = episode
            elif new_nsc == highest_match_nsc and new_sc > highest_match_sc:
                highest_match_nsc = new_nsc
                highest_match_sc = new_sc
                ep_name_new = episode

            #print("THISssssssssss         ", ep_info)

            old_sc, old_nsc = old_get_jaccard_sim(storySent, wxques)
            scList[episode] = old_sc
            nscList[episode] = old_nsc
            #ep_info = [old_sc, transliterate_query_mv, episode_mv]
            #test_list_old.append(ep_info)
            if old_sc > highest_match_old:
                highest_match_old = old_sc
                ep_name_old = episode
            #print("OLDDDD", ep_name_old)
            #print("NEWWWW", ep_name_new)

            ansfile.write("old_ep: " + str(ep_name_old) + "new_ep: " + str(ep_name_new))

    if matchEntity=="new":
        print("episode name new ", ep_name_new)
    return ep_name_new


def run_analysis(fno,ultimateList, question_num):
    qfp = open("stories/Questions/story"+fno, "r")
    questions = qfp.readlines()
    for question in questions:
        wxquestion = transliterate(question, xsanscript.DEVANAGARI, xsanscript.HK)
        question_num+=1
        for word in wxquestion.split():
            hin_word=transliterate(word, xsanscript.HK, xsanscript.DEVANAGARI)
            for val, items in questionTypes1.items():
                if hin_word in items:
                    ultimateList[val]+=1

    return question_num




questionTypes1 = {}
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
# questionTypes1['Given'] = [""]

questionTypes = {}
ultimateList = {}
for key, value in questionTypes1.items():
    questionTypes[key] = []
    temp = []
    for ques in value:
        temp.append(transliterate(ques, xsanscript.DEVANAGARI, xsanscript.HK))
    questionTypes[key] = temp
    ultimateList[key] = 0

frange = ['1', '2', '11', '12', '13', '14']
#num_of_questions=0
#frange = ['2']
for fno in frange:
    answerfile=open("WithNewJaccardAnswers"+fno, 'w')
    fname = "stories/Questions/story" + fno
    SGname = "anaandverbanaresolvedStoryGrammar" + fno + ".json"
    readingFiles(fname, SGname, answerfile)
    print("________________________________________")
    answerfile.close()
    #num_of_questions+=run_analysis(fno, ultimateList,0)
    #print("THIS IS NUMBER      ",num_of_questions)
    #print("ultimateLIST        ", ultimateList)
# print("Done")
# quesComparision.close()

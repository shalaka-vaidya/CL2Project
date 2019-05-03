# -*- coding: utf-8 -*-

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

data = {}
main_template={"relation": "main"}
karta_template = {"relation": "k1"}
karma_template = {"relation": "k2"}
prep_template = {"relation": "lwg__psp"}
adj_template = {"relation": "nmod__adj"}
r6_template = {"relation": "r6"}
adv_template = {"relation": "adv"}
rcp1_template = {"relation": "k4"}
rcp2_template = {"relation": "k4a"}
intf_template = {"relation": "jjmod__intf"}
k1s_template = {"relation": "k1s"}
pof_template = {"relation": "pof"}
k7_template = {"relation": "k7"}

def relationDic(tree):
	pcrelation=[]
	for i in range(len(tree)):
		sublist=[]
		sublist.append(int(tree[i][0]))
		sublist.append(tree[i][6])
		sublist.append(tree[i][7])
		pcrelation.append(sublist)
	return pcrelation
	
def childrenConfig(tree):
	for i in range(len(tree)):
		tree[i].append([])
		tree[i][0]=int(tree[i][0])
		tree[i][6]=int(tree[i][6])
		#tree[6]=int(tree[6])
	for i in range(len(tree)):
		parentId=tree[i][6]
		if (parentId !=0):
			tree[int(parentId)-1][-1].append(i+1)
	return tree

def graphMaking(tree):
	graph = nx.DiGraph()
	plt.figure()
	labelDic = {}
	nodeLabels = {}
	nodeLabels['0'] = "dummy"
	for word in tree:
		#print(word)
		nodetup = (word[0], word[6])
		graph.add_edge(nodetup[1], nodetup[0])
		graph[nodetup[1]][nodetup[0]]["relation"] = word[7]
		labelDic[nodetup] = word[7]
		actualWord = word[1]
		nodeLabels[nodetup[0]] = transliterate(actualWord, xsanscript.DEVANAGARI, xsanscript.HK)
	pos = nx.spring_layout(graph)
	nx.draw(graph, pos, edge_color='black', width=1, linewidths=1, node_size=500, node_color='pink', alpha=0.9, labels=nodeLabels)
	nx.draw_networkx_edge_labels(graph, pos, edge_labels=labelDic)
	plt.axis('off')
	#plt.show()
	return graph, nodeLabels
		

def printMainVerb(tree):
	for word in tree:
		if word[7] == 'main':
			return word

def templateReturn(template, neighbours):
	result=[]
	flag=1
	for neighbour, relation in neighbours.items():
		if relation==template:
			result.append(neighbour)
			flag=0
	if flag==1:
		result=[-1]
	return result

def populateData(graph,nodeLabels,episode_title):
	neighbours=graph['0']
	karta_prepList = []
	karta_adjList = []
	karma_prepList = []
	karma_adjList = []
	mainVerb=templateReturn(main_template, neighbours)

	edges_data = graph.edges.data()
	for edge in edges_data:
		if edge[2]['relation'] == 'k7t':
			adj_time = templateReturn(adj_template, graph[edge[1]])
			#data[episode_title]['time'] = (adj_time[0], edge[1])
			adv_time = templateReturn(adv_template, graph[edge[1]])
			r6_time = templateReturn(r6_template,graph[edge[1]])
			time_sent=""
			if adj_time[0]!=-1:
				time_sent+=nodeLabels[adj_time[0]]+' '
			if adv_time[0]!=-1:
				time_sent+=nodeLabels[adv_time[0]]+' '
			if r6_time[0] != -1:
				time_sent += nodeLabels[r6_time[0]]+' '
			time_sent+=nodeLabels[edge[1]]
			data[episode_title]['time'] = time_sent
		if edge[2]['relation'] == 'k7p':
			adj_place = templateReturn(adj_template, graph[edge[1]])
			prep_place = templateReturn(prep_template, graph[edge[1]])
			#data[episode_title]['location'] = (adj_place[0], edge[1], prep_place[0])
			place_sent=''
			if adj_place[0] == -1:
				place_sent = ""
			else:
				place_sent += nodeLabels[adj_place[0]]
			place_sent += " " + nodeLabels[edge[1]]
			if prep_place[0] == -1:
				place_sent = ""
			else:
				place_sent += " "+nodeLabels[prep_place[0]]
			data[episode_title]['location']=place_sent
	if mainVerb[0]!=-1 and nodeLabels[mainVerb[0]]!='hai':
		mainverb_neigbours=graph[mainVerb[0]]
		karta=templateReturn(karta_template,mainverb_neigbours)
		karma=templateReturn(karma_template,mainverb_neigbours)
		#print("KARTA", karta)
		for singleKarta in karta:
			if singleKarta!=-1:
				karta_prepList.append([singleKarta, templateReturn(prep_template, graph[singleKarta])])
				karta_adjList.append([singleKarta, templateReturn(adj_template, graph[singleKarta])])
		#print("kartaprepList", karta_prepList)
		#print("kartaadjList", karta_adjList)
		for singleKarma in karma:
			if singleKarma != -1:
				karma_prepList.append([singleKarma, templateReturn(prep_template, graph[singleKarma])])
				karma_adjList.append([singleKarma, templateReturn(adj_template, graph[singleKarma])])
		#print("karmaprepList", karma_prepList)
		#print("karmaadjList", karma_adjList)
		data[episode_title]['kartaprep'] = karta_prepList
		data[episode_title]['kartaadj'] = karta_adjList
		data[episode_title]['karmaprep'] = karma_prepList
		data[episode_title]['karmaadj'] = karma_adjList
		#print("sent", data[episode_title]['actual_sentence'])
		#print("KARTA_adj", karta_prepList)

	#time and place populating

def parsing(fname):
	fp = open(fname, "r")
	splitter = [",", "अौर", "कि", "पर", "कर"]
	text = fp.read()
	sent = re.split('।', text)
	parser = Parser(lang='hin')
	epi_key=0
	for i in range(len(sent)):
		flag_comma = 0
		if (sent[i] != "\n"):
			if any(split in sent[i] for split in splitter):
			#if (',' in sent[i]):
				flag_comma=1
			subset_sent=re.split(',|अौर|कि|पर|कर', sent[i])
			for subsent in subset_sent:
				words = subsent.split()
				tree = parser.parse(words)
				for word in tree:
					word[1]=transliterate(word[1], xsanscript.DEVANAGARI, xsanscript.HK)
					word[2]=transliterate(word[2], xsanscript.DEVANAGARI, xsanscript.HK)
				graph, nodelabels = graphMaking(tree)
				Episode_Title = epi_key
				epi_key += 1
				data[Episode_Title] = {}
				data[Episode_Title]={
					'sentence_id': str(Episode_Title),
					'actual_sentence': transliterate(subsent, xsanscript.DEVANAGARI, xsanscript.HK),
					'time': 'tbd',
					'location': 'tbd',
					'karta': 'tbd',
					'given': 'tbd',
					'new': 'tbd',
					'kartaprep': 'tbd',
					'kartaadj': 'tbd',
					'karmaprep': 'tbd',
					'karmaadj': 'tbd',
					'parser_output': tree,
				}
				print("actual", data[Episode_Title]['actual_sentence'])
				if flag_comma==1 and subset_sent[0]!=subsent:
					data[Episode_Title]['given']=transliterate(subset_sent[subset_sent.index(subsent)-1], xsanscript.DEVANAGARI, xsanscript.HK)
					data[Episode_Title]['new']=transliterate(subsent, xsanscript.DEVANAGARI, xsanscript.HK)
				populateData(graph, nodelabels, Episode_Title)


				#print("DATAAA", data)

	for key in data.keys():
		if data[key]['time']=='tbd' and key!=0:
			data[key]['time']=data[key-1]['time']
		if data[key]['location'] == 'tbd' and key != 0:
			data[key]['location'] = data[key-1]['location']
		if (len(data[key]['kartaprep'])!=0 and data[key]['kartaprep']!='tbd' ):
			par_index=int(data[key]['kartaprep'][-1][0])
			if data[key]['parser_output'][par_index-1][3]=='PRP':
				data[key]['karta'] = [par_index,data[key-1]['karta'][1]]
			else:
				data[key]['karta'] = [par_index,transliterate(data[key]['parser_output'][par_index-1][1], xsanscript.DEVANAGARI, xsanscript.HK)]
	"""print()
	print('DATAAAAAAAAAAAA')
	for singleData, val in data.items():
		print(singleData, val)"""
	"""for mainVerb in listMainVerb:
		print(mainVerb)
	"""
	return(data)
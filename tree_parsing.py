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
	graph=nx.DiGraph()
	plt.figure()
	labelDic={}
	nodeLabels={}
	nodeLabels['0']="dummy"
	for word in tree:
		#print(word)
		nodetup=(word[0],word[6])
		graph.add_edge(nodetup[1],nodetup[0])
		graph[nodetup[1]][nodetup[0]]["relation"]=word[7]
		labelDic[nodetup]=word[7]
		actualWord=word[1]
		nodeLabels[nodetup[0]]=transliterate(actualWord, xsanscript.DEVANAGARI, xsanscript.HK)
	pos=nx.spring_layout(graph)
	nx.draw(graph,pos,edge_color='black',width=1,linewidths=1,node_size=500,node_color='pink',alpha=0.9,labels=nodeLabels)
	nx.draw_networkx_edge_labels(graph,pos,edge_labels=labelDic)
	plt.axis('off')
	#plt.show()
	return graph, nodeLabels
		

def printMainVerb(tree):
	for word in tree:
		if (word[7]=='main'):
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
	main_template={"relation": "main"}
	karta_template = {"relation": "k1"}
	karma_template = {"relation": "k2"}
	prep_template = {"relation": "lwg__psp"}
	adj_template = {"relation": "nmod__adj"}
	karta_prepList = []
	karta_adjList = []
	karma_prepList = []
	karma_adjList = []
	mainVerb=templateReturn(main_template, neighbours)

	edges_data = graph.edges.data()
	for edge in edges_data:
		if edge[2]['relation'] == 'k7t':
			adj_time = templateReturn(adj_template, graph[edge[1]])
			data[episode_title]['time'] = (adj_time[0], edge[1])
		if edge[2]['relation'] == 'k7p':
			adj_place = templateReturn(adj_template, graph[edge[1]])
			prep_place = templateReturn(prep_template, graph[edge[1]])
			data[episode_title]['location'] = (adj_place[0], edge[1], prep_place[0])

	if mainVerb[0]!=-1 and nodeLabels[mainVerb[0]]!='hai':
		mainverb_neigbours=graph[mainVerb[0]]
		karta=templateReturn(karta_template,mainverb_neigbours)
		karma=templateReturn(karma_template,mainverb_neigbours)
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
		data[episode_title]['kartaprep']=karta_prepList
		data[episode_title]['kartaadj'] = karta_adjList
		data[episode_title]['karmaprep'] = karma_prepList
		data[episode_title]['karmaadj'] = karma_adjList

	#time and place populating

#print("HAHAHAHA", graph.edges.data())
	#print(graph.edges_iter(data='relation'))

def parsing(fname):
	fp = open(fname,"r")
	text = fp.read()
	#sent=text.split("।")
	sent=re.split('।|,',text)
	parser = Parser(lang='hin')
	listMainVerb=[]
	for i in range(len(sent)):
		if (sent[i] != "\n"):
			print ("SENTENCE", sent[i])
			words=sent[i].split()
			tree= parser.parse(words)
			print(tree)
			graph, nodelabels=graphMaking(tree)
			"""mainWord=printMainVerb(tree)
			if mainWord is not None:
				listMainVerb.append(mainWord)"""
			"""treeWithChildren= childrenConfig(tree)
			for wordInfo in treeWithChildren:
				print(wordInfo)
			print();
			patrentChild=[]
			parentChildRelation=relationDic(treeWithChildren)
			for wordInfo in parentChildRelation:
				print(wordInfo)
			print()"""


			Episode_Title = "episode" + "_" + str(i)
			data[Episode_Title] = {}
			data[Episode_Title]={
				'sentence_id': str(i),
				"actual_sentence": transliterate(sent[i], xsanscript.DEVANAGARI, xsanscript.HK),
				'time': 'tbd',
				'location': 'tbd',
				'kartaprep': 'tbd',
				'kartaadj': 'tbd',
				'karmaprep': 'tbd',
				'karmaadj': 'tbd',
			}
			populateData(graph, nodelabels, Episode_Title)
			print(data[Episode_Title])
			
	print()
	print('DATAAAAAAAAAAAA')
	for singleData, val in data.items():
		print(singleData, val)
	"""for mainVerb in listMainVerb:
		print(mainVerb)
	"""
def main():
	fname="../../stories/story2"
	parsing(fname)
	with open('StoryGrammer.json', 'w') as outfile:
		json.dump(data, outfile)
	
main()

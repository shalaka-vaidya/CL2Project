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
	graph=nx.Graph();
	plt.figure()
	labelDic={}
	nodeLabels={}
	nodeLabels['0']="dummy"
	for word in tree:
		#print(word)
		nodetup=(word[0],word[6])
		graph.add_edge(nodetup[0],nodetup[1])
		labelDic[nodetup]=word[7]
		actualWord=word[1]
		nodeLabels[nodetup[0]]=transliterate(actualWord, xsanscript.DEVANAGARI, xsanscript.HK)
	pos=nx.spring_layout(graph)
	nx.draw(graph,pos,edge_color='black',width=1,linewidths=1,node_size=500,node_color='pink',alpha=0.9,labels=nodeLabels)
	nx.draw_networkx_edge_labels(graph,pos,edge_labels=labelDic)
	plt.axis('off')
	plt.show()
	return graph
		

def printMainVerb(tree):
	for word in tree:
		if (word[7]=='main'):
			return word
			
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
			graph=graphMaking(tree)
			mainWord=printMainVerb(tree)
			if mainWord is not None:
				listMainVerb.append(mainWord)
			"""treeWithChildren= childrenConfig(tree)
			for wordInfo in treeWithChildren:
				print(wordInfo)
			print();
			patrentChild=[]
			parentChildRelation=relationDic(treeWithChildren)
			for wordInfo in parentChildRelation:
				print(wordInfo)
			print()"""
			
	print()
	for mainVerb in listMainVerb:
		print(mainVerb)
	
def main():
	fname="../../stories/story1"
	parsing(fname)
	
main()

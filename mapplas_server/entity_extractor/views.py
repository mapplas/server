import sys
import nltk

from nltk.corpus import treebank
#from nltk.corpus import conll2000

from rest_api.models import Application


def load():

	first_app_list = Application.objects.all()[:1000]
	
	for app in first_app_list:
		
		name = app.app_name
		name = name.encode('utf-8')
		
		'''
		description = app.app_description
		description = description.encode('utf-8')
		'''
		
		grammar = r"""
					  NP: {<NN.*>+}          # Chunk sequences of NN
				  """
		cp = nltk.RegexpParser(grammar)
		
		sentences = parse(name)
		tree = cp.parse(sentences[0])
	
		for node in tree:
			if hasattr(node, 'node'):
				if node.node == 'NP':
					listOfWords = [] 
					for element in node:
						listOfWords.append(element[0])
					
					print (listOfWords)
					
					
					
					
'''
sentences = parse(description)
train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])

for sent in sentences:
	chunk_parser = ChunkParser(train_sents)
	tree = chunk_parser.parse(sent)
	
	for subtree in tree.subtrees(filter=lambda t: t.node == 'NP'):
	    # print the noun phrase as a list of part-of-speech tagged words
	    # print subtree.leaves()
	    for chunk in nltk.ne_chunk(subtree.leaves()):
	    	if hasattr(chunk, 'node'): 
				if chunk.node == "GPE":
					print(chunk)
'''
		
	
	
def parse(document):
	sentences = nltk.sent_tokenize(document) 
	sentences = [nltk.word_tokenize(sent) for sent in sentences] 
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	
	return sentences
	
'''	
class ChunkParser(nltk.ChunkParserI):
	def __init__(self, train_sents):
		train_data = [[(t,c) for w,t,c in nltk.chunk.util.tree2conlltags(sent)]
		for sent in train_sents]
		self.tagger = nltk.TrigramTagger(train_data)
		
	def parse(self, sentence):
		pos_tags = [pos for (word,pos) in sentence]
		tagged_pos_tags = self.tagger.tag(pos_tags)
		chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
		conlltags = [(word, pos, chunktag) for ((word,pos),chunktag)
		in zip(sentence, chunktags)]
		return nltk.chunk.util.conlltags2tree(conlltags)
'''
import sys
sys.path.append('/home/ubuntu/ENV/lib/python3.2/site-packages/nltk-3.0a0')
#sys.path.append('/usr/local/lib/python3.2/dist-packages/nltk-3.0a0-py3.2.egg')
import nltk

from nltk.corpus import treebank

from rest_api.models import Application


def first_apps_names():
	first_app_list = Application.objects.all()[:100]

	sentence = preprocess(first_app_list[1].app_name)
	#print(sentence)
	
	'''
	for app in first_app_list:
		sentences = preprocess(app.app_name)
		print (sentences)
	'''
#		sent = nltk.corpus.treebank.tagged_sents()[app]
#		print (nltk.ne_chunk(sent, binary=True))
	
	
def preprocess(document):
	sentences = nltk.sent_tokenize(document)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	print (sentences)
	#return sentences
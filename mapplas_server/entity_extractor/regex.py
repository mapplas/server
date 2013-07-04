import sys, mmap, re

from datetime import date
from rest_api.models import Application


def load():

	# Define grammar
	grammar = r"""
				  NP: {<NN.*>+}          # Chunk sequences of NN
			  """
	cp = nltk.RegexpParser(grammar)
	
	# Open geonames file
	geonames_file = open('/home/ubuntu/nltk_data/corpora/gazetteers/geonames_names.txt', "r")

	# Get app array
	first_app_list = Application.objects.all()[:500]
	
	for app in first_app_list:
		
		name = app.app_name
		name = name.encode('utf-8')
		
		'''
		description = app.app_description
		description = description.encode('utf-8')
		'''
		
		sentences = parse(name)
		tree = cp.parse(sentences[0])
	
		for node in tree:
			if hasattr(node, 'node'):
				if node.node == 'NP':
					wordAppend = ""
					for element in node:
						wordAppend = wordAppend + ' ' + element[0]
					
					print(wordAppend)
						
					for line in geonames_file:
						if wordAppend in line:
							print('!!!!!!!!!!! ' + wordAppend + ' ' + name)
							break
	
	geonames_file.close()	
	
	
def parse(document):
	sentences = nltk.sent_tokenize(document) 
	sentences = [nltk.word_tokenize(sent) for sent in sentences] 
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	
	return sentences
	
'''
Gets a string and checks if 4 digit numbers appears on it. (year)
If matches only one number, compares it with current year. If smaller, returns false.
If matches more than a number, if all are smaller than current year, returns false.
'''
def is_valid_title_checking_years(title):

	current_year = date.today().year
	
	pattern = re.compile('(\d{4})+')
	matches = pattern.findall(title)
	
	number_of_matches = len(matches)
	
	if number_of_matches != 0:
	
		# One match
		if number_of_matches == 1:
			if int(matches[0]) < int(current_year):
				return False
			else:
				return True
			
		# More than one match
		else:
		
		 	for match in matches:
		 		if int(match) >= int(current_year):
		 			return True
		 	
		 	return False
	else:
		return True
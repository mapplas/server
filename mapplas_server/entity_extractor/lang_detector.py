import nltk

from nltk.corpus import treebank


SPANISH_STOPWORDS = set(nltk.corpus.stopwords.words('spanish'))
NON_SPANISH_STOPWORDS = set(nltk.corpus.stopwords.words()) - SPANISH_STOPWORDS
 
STOPWORDS_DICT = {lang: set(nltk.corpus.stopwords.words(lang)) for lang in nltk.corpus.stopwords.fileids()}


'''
Returns 'spanish' string for spanish text.
''' 
def get_language(text):
    words = set(nltk.wordpunct_tokenize(text.lower()))
    return max(((lang, len(words & stopwords)) for lang, stopwords in STOPWORDS_DICT.items()), key = lambda x: x[1])[0]
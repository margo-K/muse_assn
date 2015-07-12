import nltk
import bs4
import json
from datetime import datetime
import pdb
import string
import numpy as np
import re

def get_list_items(text):
	p = re.compile('<li>(.*?)</li>')
	list_items = p.findall(text)

def get_quarter(datetime):
	year, month = datetime.year, datetime.month
	quarter = (month-1)//3+1
	return "Q{}Y{}".format(quarter,year)

class CategoryError(Exception):
	def __init__(self,value):
		self.value = value

	def __str__(self):
		return repr(self.value)

def _tokenize_listing(listing,date_func,stopwords=nltk.corpus.stopwords.words('English') + list(string.punctuation)):#need to add category, time_period
	"""Returns a set of tokens in the listing, along with the listing's category and date"""
	date = date_func(datetime.strptime(listing['creation_date'],'%Y-%m-%d'))

	category = listing['categories']#Note: takes each category as a list.
	if type(category) !=list:
		raise CategoryError("Category Error: Cannot index {}".format(listing['id'])) 
	category = tuple(category)

	description = listing['full_description']
	qualities = bs4.BeautifulSoup(description).find_all("li")
	text = ". ".join([quality.text for quality in qualities])
	tokens = [unigram.lower().strip(string.punctuation) for unigram in nltk.word_tokenize(text) if unigram not in stopwords and unigram != ""]#[item.lower().strip(string.punctuation) for item in text.split(' ') if item not in nltk.corpus.stopwords.words('English')+list(string.punctuation)]
	if '' in tokens:
		tokens.remove('')
	bigrams = set(nltk.bigrams(tokens))
	trigrams = set(nltk.trigrams(tokens))
	return set(tokens).union(bigrams).union(trigrams), category, date

def get_lexicon(listings,date_func):
	lexicon = set()
	groups = {}
	for listing in listings:
		tokens, category, date = _tokenize_listing(listing,date_func)
		lexicon.union(tokens)
		group_listings = groups.setdefault((category,date),[])
		group_listings.append((tokens))
	print "Grouped all listings"
	print len(groups)
	total_words = len(lexicon)
	lexicon_indexes = {word: index for index, word in enumerate(lexicon)}
	for group_name, listings_tokens in groups.iteritems():
		groups[group_name] = [_get_vectorized_listing(tk) for tk in listings_tokens]
	return lexicon_indexes, groups #could be the OO values


def _get_vectorized_listing(listing_tokens,lexicon_indexes):
	print len(lexicon_indexes)
	v_listing = np.zeros(len(lexicon_indexes))
	for token in listing_tokens:
		pdb.set_trace()
		v_listing[lexicon_indexes[token]]+=1
	return v_listing


def get_probabilities(group):
	"""Given a matrix of document-word vectors for a time period,
	return a probability vector for which each element is the probability of 
	seeing that word in that time period

	Ex: Suppose we have a lexicon like ["big", "dog", "jumps" "high"]
		d1 = np.array([1,1,1,0]) => ["big","dog","jumps"]
		d2 = np.array([0,1,1,1]) => ["dog","jumps","high"]
		m = np.array([d1,d2])

		get_probabilities(m)
		=> array([ 1. ,  1. ,  1. ,  0.5])
		=> P("big") = 1
		=> P("dog") = 1
		=> P("jumps") = 1
		=> P("high") = .5 """

	return np.mean(group,axis=0)


if __name__ == '__main__':
	with open('data/listings.json','r') as f:
		listings = json.load(f)
		lexicon_indexes, groups = get_lexicon(listings,date_func=lambda x: x.year)
	pdb.set_trace()

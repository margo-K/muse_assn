from __future__ import division
import nltk
import json
import pdb
import string
import numpy as np
import itertools
import sys

from fetcher import fetch_listings
from helpers import get_list_items, get_date, trunc_date

def _tokenize_listing(listing,time_period,stopwords=nltk.corpus.stopwords.words('English') + list(string.punctuation)):#need to add category, time_period
	"""Returns a set of tokens in the listing, along with the listing's category and date"""
	date = trunc_date(get_date(listing['creation_date']),time_period)

	category = listing['categories']#Note: takes each category as a list.
	if type(category) !=list:
		raise CategoryError("Category Error: Cannot index {}".format(listing['id'])) 
	category = tuple(category)

	description = listing['full_description']
	qualities = get_list_items(description)
	if not qualities:
		return set(),[],""#this is in the case where there's no data to index

	text = ". ".join([quality for quality in qualities])
	tokens = [unigram.lower().strip(string.punctuation) for unigram in nltk.word_tokenize(text) if unigram not in stopwords and unigram != ""]#[item.lower().strip(string.punctuation) for item in text.split(' ') if item not in nltk.corpus.stopwords.words('English')+list(string.punctuation)]
	if '' in tokens:
		tokens.remove('')
	bigrams = set(nltk.bigrams(tokens))
	trigrams = set(nltk.trigrams(tokens))
	return set(tokens).union(bigrams).union(trigrams), category, date

def get_lexicon(listings,time_period):
	lexicon = set()
	groups = {}
	un_indexed = 0
	for listing in listings:
		tokens, category, date = _tokenize_listing(listing,time_period)
		if not tokens:
			un_indexed +=1
		else:
			lexicon |=tokens
			group_listings = groups.setdefault(category,{})
			category_date_listings = groups[category].setdefault(date,[])
			try:
				groups[category][date].append(tokens)
			except:
				pdb.set_trace()
	print "Total Categories {}".format(len(groups))
	total_words = len(lexicon)
	lexicon_indexes = {word: index for index, word in enumerate(lexicon)}
	size = len(lexicon_indexes)

	for category, date_groups in groups.iteritems():
		for date, listings in date_groups.iteritems():
			groups[category][date] = [_get_vectorized_listing(listing,lexicon_indexes,size) for listing in listings]
	print "Total not indexed {}".format(un_indexed)
	print "Portion not indexed: {}".format(un_indexed/len(listings))
	return lexicon_indexes, groups #could be the OO values

def _get_vectorized_listing(listing_tokens,lexicon_indexes,lexicon_size):
	"""Takes a set of tokens for a listing, a lexicon and the lexicon_size and returns
	the vector representation of the numpy array, where each element is a word
	in the lexicon and each value is 0 or 1, depending on whether the word appears in the listing """

	v_listing = np.zeros(lexicon_size)
	for token in listing_tokens:
		index = lexicon_indexes[token]
		v_listing[index]+=1
	if lexicon_size !=len(lexicon_indexes):
		pdb.set_trace
	return v_listing

def get_probabilities(listings_group):
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

	return np.mean(listings_group,axis=0)

def biggest_change(sorted_group_probabilities,limit):
	"""Takes in an ordered list, group_probabilities, calculates the average of the last n-1 periods
	and returns the indices of the n top words (n <= limit) with the 
	largest positive difference between the last period and the previous average

	Ex: lexicon = ["big", "dog", "jumps" "high"]
		group_probabilities = [array([0, 1, 1, 1]),
 		array([ 0.5,  1. ,  1. ,  1. ]),
 		array([ 1. ,  0.5,  0.5,  0.5])]
 		=> [0]
 """
 	#Add case when there's only one, in case it's sparse
 	if sorted_group_probabilities[:-1]:
 		old_average = np.mean(sorted_group_probabilities[:-1],axis=0)
 	else:
 		old_average = np.zeros(len(sorted_group_probabilities[-1]))
 	deltas = sorted_group_probabilities[-1]-old_average
 	sorted_indices = np.argsort(deltas)
 	trending = itertools.takewhile(lambda x: deltas[x]>0,sorted_indices)
	top_trending = itertools.islice(trending,0,limit)
	return top_trending

def get_trending(category_listings,trending_function=biggest_change,limit=10):
	"""Takes the data for a category and outputs a generator of the indices
	of trending items,where trending is defined by the trending_function

	Ex: {datetime.date(2012, 1, 1): [[1,1,1,1], [0,1,1,1]], => P(2012) = [.5,1,1,1]
		 datetime.date(2013, 1, 1): [[1,1,0,0], [1,0,1,1]]} => P(2013) = [1,.5,.5,.5]

		 =>  generator([0]), b/c the first element is the only one with a positive change """
	
	group_probabilities = [get_probabilities(category_listings[time_period]) for time_period in sorted(category_listings.keys())]
	return trending_function(group_probabilities,limit)

def main(data_file='data/listings.json',time_period='year'):
	if data_file:
		with open(data_file,'r') as f:
			listings = json.load(f)
	else:
		listings = fetch_listings()

	lexicon_indexes, groups = get_lexicon(listings,time_period=time_period)
	for category, category_listings in groups.iteritems():
		trending = get_trending(category_listings)
		print "Category {} Trends\n".format(category)
		for index in trending:
			for word, word_index in lexicon_indexes.iteritems():
				if index == word_index:
					print word
		# for word_or_phrase in trending:
		# 	print ' '.join(word_or_phrase)

if __name__ == '__main__':
	main()




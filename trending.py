from __future__ import division
import nltk
import json
import pdb
import string
import numpy as np
import itertools
import sys
import datetime

from fetcher import fetch_listings
from helpers import get_list_items, get_date, trunc_date

def _parse_listing(listing,bigrams=True,trigrams=False,stopwords=None):
	"""Returns a set of tokens in the listing, along with the listing's category and date"""
	if not stopwords:
		stopwords = nltk.corpus.stopwords.words('English') + list(string.punctuation)
	category = listing['categories']#Note: takes each category as a list.	
	description = listing['full_description']
	qualities = get_list_items(description)
	if not qualities or not category:
		return set(),[],"" 

	text = ". ".join([quality for quality in qualities])
	tokens = [token.lower().strip(string.punctuation) for token in text.split(' ') if token not in stopwords] 
	all_tokens = set(tokens)
	all_tokens.discard('')
	if bigrams:
		all_tokens |= set(nltk.bigrams(tokens))
	if trigrams:
		all_tokens |= set(nltk.trigrams(tokens))
	return all_tokens, category , listing['creation_date']

def get_lexicon(listings):
	word_counter, un_indexed = 0, 0
	lexicon_index = {}
	lexicon, parsed_listings = [], []
	
	print "Building lexicon ..."
	for listing in listings:
		tokens, categories, date = _parse_listing(listing)
		if tokens:
			int_tokens = []
			for token in tokens:
				token_index = lexicon_index.get(token)
				if not token_index:
					token_index = lexicon_index.setdefault(token,word_counter)
					word_counter +=1
					lexicon.append(token)
				int_tokens.append(token_index)
			parsed_listings.append((int_tokens,categories,date))
		else:
			un_indexed +=1

	print "Total not indexed {}".format(un_indexed)
	print "Portion not indexed: {}".format(un_indexed/len(listings))
	return lexicon, parsed_listings

def _group_listings(parsed_listings,lexicon_size,time_period):
	groups = {}
	for (int_tokens, categories, date) in parsed_listings:
		date_period = trunc_date(get_date(date),time_period)
		vector_listing = _get_vectorized_listing(int_tokens,lexicon_size)
		for category in categories:
			group_listings = groups.setdefault(category,{})
			category_date_listings = groups[category].setdefault(date,[])
			groups[category][date].append(vector_listing)
	return groups

def _get_vectorized_listing(int_tokens,lexicon_size):
	"""Takes a list of word indexes for a listing and a lexicon_size and returns
	the vector representation of the numpy array, where each element is a word
	in the lexicon and each value is 0 or 1, depending on whether the word appears in the listing """
	l = np.zeros(lexicon_size)
	for int_token in int_tokens:
		l[int_token] +=1
	return l

def _get_probabilities(listings_group):
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
 	trending = itertools.takewhile(lambda x: deltas[x]>0,sorted_indices[::-1])
	top_trending = itertools.islice(trending,0,limit)
	return top_trending

def get_trending(category_listings,trending_function=biggest_change,limit=10):
	"""Takes the data for a category and outputs a generator of the indices
	of trending items,where trending is defined by the trending_function

	Ex: {datetime.date(2012, 1, 1): [[1,1,1,1], [0,1,1,1]], => P(2012) = [.5,1,1,1]
		 datetime.date(2013, 1, 1): [[1,1,0,0], [1,0,1,1]]} => P(2013) = [1,.5,.5,.5]

		 =>  generator([0]), b/c the first element is the only one with a positive change """
	
	group_probabilities = [_get_probabilities(category_listings[time_period]) for time_period in sorted(category_listings.keys())]
	return trending_function(group_probabilities,limit)

def main(data_file='data/listings.json',time_period='year'):
	if data_file:
		with open(data_file,'r') as f:
			listings = json.load(f)
	else:
		listings = fetch_listings()

	lexicon, parsed_listings = get_lexicon(listings)
	groups = _group_listings(parsed_listings,len(lexicon),time_period)
	print "Trending Items {} to {}".format(time_period,time_period)
	for category, category_listings in groups.iteritems():
		trending = get_trending(category_listings)
		print "\n{}\n===========".format(category)
		for rank, index in enumerate(trending):
			word_or_phrase = lexicon[index]
			if type(word_or_phrase) == tuple:
				word_or_phrase = " ".join(word_or_phrase)
			print "{}. {}".format(rank+1,word_or_phrase.encode('utf-8'))

if __name__ == '__main__':
	main()




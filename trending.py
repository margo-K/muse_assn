from __future__ import division
import os
import sys
import datetime
import json
import numpy as np

from fetcher import fetch_listings
from helpers import get_date, trunc_date, get_vectorized_listing, get_probabilities
from trending_metrics import biggest_change
from parsers import existence_parse


class TrendFinder(object):
	def __init__(self,listings,parse_fn=existence_parse):
		self._listings = listings
		self._groups = {}
		self._lexicon = []
		self._parse_fn = parse_fn

	def make_lexicon(self):
		"""Returns a lexicon of the entire set of listings and a list of parsed
		listing records"""
		word_counter, un_indexed = 0, 0
		lexicon_index = {}
		self._parsed_listings = []
		
		print "Building lexicon ..."
		for listing in self._listings:
			tokens, categories, date = self._parse_fn(listing)
			if tokens:
				int_tokens = []
				for token in tokens:
					token_index = lexicon_index.get(token)
					if not token_index:
						token_index = lexicon_index.setdefault(token,word_counter)
						word_counter +=1
						self._lexicon.append(token)
					int_tokens.append(token_index)
				self._parsed_listings.append((int_tokens,categories,date))
			else:
				un_indexed +=1

		print "Total not indexed {}".format(un_indexed)
		print "Portion not indexed: {}".format(un_indexed/len(self._listings))

	def _group_listings(self,time_period):#parsed may or may not be an attribute
		"""Returns a nested dictionary of grouped, vectorized listings, where the 
		groups are categories then time periods

		Ex: 
		lexicon = ["big","dog","barks","loudly]
		parsed_listings = [([1,2],'business','2012-01-12'), ([1,3],'business',2013-03-01'),
							([0,1,2],'marketing','2014-04-01'),([0,2],'marketing','2013-01-01')]
		group_listings(parsed_listings,lexicon_size=4,time_period='year')

		=> {"business": {datetime.date(2012, 1, 1): [[0,1,1,0]],datetime.date(2013, 1, 1): [[0,1,0,1]]}, 
			"marketing":{datetime.date(2013, 1, 1):[[0,0,1,0]] , datetime.date(2014, 1, 1): [[1,1,1,0]]}}"""
		lexicon_size = len(self._lexicon)
		for (int_tokens, categories, date) in self._parsed_listings:
			date_period = trunc_date(get_date(date),time_period)
			vector_listing = get_vectorized_listing(int_tokens,lexicon_size)
			for category in categories:
				group_listings = self._groups.setdefault(category,{})
				category_date_listings = self._groups[category].setdefault(date_period,[])
				self._groups[category][date_period].append(vector_listing)

	def _get_trending(self,category_listings,current_period,time_period,trending_function,limit=10):
		"""Takes the data for a category and outputs a generator of the indices
		of trending items,where trending is defined by the trending_function

		Ex: {datetime.date(2012, 1, 1): [[1,1,1,1], [0,1,1,1]], => P(2012) = [.5,1,1,1]
			 datetime.date(2013, 1, 1): [[1,1,0,0], [1,0,1,1]]} => P(2013) = [1,.5,.5,.5]

			 =>  generator([0]), b/c the first element is the only one with a positive change """

		if current_period not in category_listings.keys():
			print "No listings for this period"
			return []

		current_period_probabilities = get_probabilities(category_listings[current_period])
		periods = category_listings.keys()
		periods.remove(current_period)

		past_period_probabilities = [get_probabilities(category_listings[period]) for period in periods]
		return trending_function(current_period_probabilities,past_period_probabilities,limit)

	def get_report(self,time_period,current_period=None,trending_function=biggest_change):
		self._group_listings(time_period)
		print "\nTrending Items: {}".format(time_period)
		if not current_period:
			current_period = trunc_date(datetime.datetime.now().date(),time_period)
		print "Current Period: {}".format(current_period)

		for category, category_listings in self._groups.iteritems():
			print "\n{}\n===========".format(category)
			trending = self._get_trending(category_listings,current_period,time_period,trending_function)
			for rank, index in enumerate(trending):
				word_or_phrase = self._lexicon[index]
				if type(word_or_phrase) == tuple:
					word_or_phrase = " ".join(word_or_phrase)
				print "{}. {}".format(rank+1,word_or_phrase.encode('utf-8'))


if __name__ == '__main__':
	if len(sys.argv) !=2:
		time_period = 'year'
	else: 
		time_period = sys.argv[1]

	if os.path.isfile('data/listings.json'):
		with open('data/listings.json','r') as f:
			listings = json.load(f)
	else:
		listings = fetch_listings()

	t = TrendFinder(listings)
	t.make_lexicon()
	t.get_report(time_period)




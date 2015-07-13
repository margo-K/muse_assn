from datetime import datetime
import numpy as np

def get_date(date_str):
	return datetime.strptime(date_str,'%Y-%m-%d').date()

def trunc_date(date,time_period):
	"""Rounds a datetime.date object to the nearest time period. 
	Supported time periods include: 'day','month','year' """
	if time_period not in ['day','month','year']:
		raise NotImplementedError
	if time_period == 'day':
		return date
	if time_period == 'month':
		return date.replace(day=1)
	if time_period == 'year':
		return date.replace(day=1,month=1)

def get_vectorized_listing(token_indices,lexicon_size):
	"""Takes a list of token indexes for a listing and a lexicon_size and returns
	the vector representation of the numpy array, where each element is a word
	in the lexicon and each value is 0 or 1, depending on whether the word appears in the listing """
	l = np.zeros(lexicon_size)
	for token_index in token_indices:
		l[token_index] +=1
	return l

def get_probabilities(word_doc_vecs):
	"""Given a list of document-word vectors for a time period,
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

	return np.mean(word_doc_vecs,axis=0)
import numpy as np
import itertools

def biggest_change(current_period_probabilities,past_periods_probabilities,limit):
	"""Returns the indices of the n top words (n <= limit) with the largest positive differences
	between the current period and the average of the past periods (or an array of zeros,
		if past_periods is an empty list)

	Ex: lexicon = ["big", "dog", "jumps" "high"]
		group_probabilities = [array([0, 1, 1, 1]),
 		array([ 0.5,  1. ,  1. ,  1. ]),
 		array([ 1. ,  0.5,  0.5,  0.5])]
 		=> [0]

 """
 	if not past_periods_probabilities:
 		old_average = np.zeros(len(current_period_probabilities))
 	else:
 		old_average = np.mean(past_periods_probabilities,axis=0)
 	deltas = current_period_probabilities-old_average
 	sorted_indices = np.argsort(deltas)
	trending = itertools.takewhile(lambda x: deltas[x]>0,sorted_indices[::-1])
	return itertools.islice(trending,0,limit)

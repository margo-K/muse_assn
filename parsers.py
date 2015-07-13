import re
import nltk
import string

def get_list_items(text):
	"""Returns all items between list tags in a text"""
	p = re.compile('<li>(.*?)</li>')
	return p.findall(text)

def existence_parse(listing,bigrams=True,trigrams=False,stopwords=None,text_func=get_list_items):
	"""Returns a set of tokens a listing, along with the listing's categories and creation date. 

	Note: frequency of occurence is not preserved """
	if not stopwords:
		stopwords = nltk.corpus.stopwords.words('English') + list(string.punctuation)
	categories = listing['categories']#Note: takes each category as a list.	
	description = listing['full_description']
	qualities = text_func(description)
	if not qualities or not categories:
		return set(),[],"" 

	text = ". ".join([quality for quality in qualities])
	tokens = [token.lower().strip(string.punctuation) for token in text.split(' ') if token not in stopwords] 
	all_tokens = set(tokens)
	all_tokens.discard('')

	if bigrams:
		all_tokens |= set(nltk.bigrams(tokens))
	if trigrams:
		all_tokens |= set(nltk.trigrams(tokens))

	return all_tokens, categories, listing['creation_date']
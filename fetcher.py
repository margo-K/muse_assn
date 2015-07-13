import requests
import json

def fetch_listings():
	first = requests.get('http://themuse.com/api/v1/jobs',params={'page':0})
	print "Got the first page"
	results = json.loads(first.text)
	max_page = results['page_count']
	listings = results['results']
	for page in xrange(1,max_page+1):
		try:
			print "Trying page {}".format(page)
			r = requests.get('http://themuse.com/api/v1/jobs',params={'page':page})
			print "Got results from page {}".format(page)
			listings.extend(json.loads(r.text)['results'])
		except Exception as e:
			print "Page {} was not retrieved".format(page)
	with open('data/listings.json', 'w') as f:
		json.dump(listings,f)
	return listings



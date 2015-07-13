from datetime import datetime
import re

def get_list_items(text):
	"""Returns all items"""
	p = re.compile('<li>(.*?)</li>')
	return p.findall(text)

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

class CategoryError(Exception):
	def __init__(self,value):
		self.value = value

	def __str__(self):
		return repr(self.value)
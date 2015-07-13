from datetime import datetime

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
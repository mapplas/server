import time
import re

from rest_api.models import Application

from urllib3 import PoolManager
from bs4 import BeautifulSoup


'''
METHOD THAT CONVERTS TIMEZONE TO SECONDS SINCE 1970
'''
def epoch(now_time):
	return time.mktime(now_time.timetuple())

'''
URL SCHEMES SCRAPPING
'''
def scrape():

	i = 1
	manager = PoolManager()
	
	while i <= 1:
		r = manager.request('GET', 'http://handleopenurl.com/api/v1.2/list.xml?apikey=e4f76a3591abb85f2369d91027f3e939&page=%d' % i)
		soup = BeautifulSoup(r.data)
		
		handleopenurl = soup.handleopenurl
		
		for bundle in soup.findAll('cfbundle'):
			scheme = unquote(bundle.urlscheme.text)
			print(scheme)
						
			displayname = unquote(bundle.displayname.text)
			print(displayname)

			try:
				app = Application.objects.get(app_name=displayname)
				if app:
					print(app)
					#app.url_schema = scheme
			except Application.DoesNotExist:
				'''
				App does not exist
				'''
		i=i+1	

def unquote(url):
  return re.compile('%([0-9a-fA-F]{2})',re.M).sub(lambda m: chr(int(m.group(1),16)), url)
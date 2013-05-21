import urllib3

'''

'''
def scrape():
	
	i = 0
	while i < 100:
		response = urllib3.request.Request('http://google.es')
		html = response.read()
		print(i)
		i=i+1
	
		

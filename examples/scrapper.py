import json
import urllib2
from bs4 import BeautifulSoup
from flask import request

### Source ###

### <1.> Returns Embed links for youtube videos with term <t>
def getvids(textToSearch = "One Piece Songs"):
	query = urllib2.quote(textToSearch)
	url = "https://www.youtube.com/results?search_query=" + query
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html,"html5lib")
	arr = set()
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
		if (not vid['href'].startswith("https://www.googleadservices.com")) and (not vid['href'].startswith("channel/")):
			arr.add(vid['href'].split("=")[-1])
    	return list(arr)

### Abstracted ###

### See <1.> 
def gv(t = "One Piece Songs"):
	return getvids(t)	

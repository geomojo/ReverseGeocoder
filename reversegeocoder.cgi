#!/usr/bin/env python
import cgi
import cgitb
import sys

from yahoogeoservices import GeoPlanetPlace
from yahoogeoservices import YahooGeoServices

cgitb.enable()
     
fields = cgi.FieldStorage()
long = None
lat = None
if fields.has_key('long'):
	long = float(fields['long'].value)

if fields.has_key('lat'):
	lat = float(fields['lat'].value)

format = 'xml'
if fields.has_key('format'):
	format_req = fields['format'].value
	if format_req.lower() == 'json':
		format = 'json'
    
text = ''

if long != None and lat != None:
	#here you might want to change the logic so that the AppID isn't in this file
	gp = YahooGeoServices("YOUR_APPID")
	places = gp.reverseGeocode(long, lat)
	if places and len(places) != 0:
		for p in places:
			place = Place(str(p[0]))
			if format == 'xml':
				text += '<place>\n<woeid>%s</woeid>\n<name>%s</name>\n<type>%s</type></place>' % (p[0], place.name,place.placeType)
			else:
				text += '{"woeid":%s, "name":"%s", "type":"%s"}' % (p[0], place.name,place.placeType)

	else:
		if format == 'xml':
			text += '<place></place>'
		else:
			text += {}
			
sys.stdout.write("Content-Length: %d\r\n" % len(text.encode('utf-8')))
sys.stdout.write("Content-Type: text/%s\r\n" % format)
sys.stdout.write("\r\n")
sys.stdout.write(text.encode('utf-8'))

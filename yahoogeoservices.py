import urllib
import math
import sys
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError


'''Module implementing a client for Yahoo\'s GeoServices
There are two classes in this module.
GeoPlanetPlace: Which is used to represent a Place with a given WoeId
YahooGeoServices: Which is used to retrive GeoPlanetPlaces from either text which is geocoded, or from coordinates.
'''

class YahooServices:

    def __init__(self, appId):
        self.appId = appId

        
class GeoPlanetPlace(YahooServices):
    baseurl = 'http://where.yahooapis.com/v1/place/'
    def __init__(self, woeid, appId):
        YahooServices.__init__(self, appId)
        self.baseparam = "appid=%s&format=xml" % self.appId
        if isinstance(woeid, int):
            self.woeid = woeid
        elif isinstance(woeid, basestring):
            self.woeid = int(woeid)
            
        if not woeid:
            return None
        url = "%s%d?%s" % (self.baseurl, self.woeid, self.baseparam)
        con = urllib.urlopen(url)
        data = con.read()
        con.close()
        self.data = data
        try:
            dom = parseString(self.data)
        except ExpatError:
            raise GeoPlanetError("Error parsing response: %s" % data)

        if dom.getElementsByTagName("centroid"):
            centroid = dom.getElementsByTagName("centroid")[0]
            self.long = float(centroid.getElementsByTagName("longitude")[0].firstChild.nodeValue)
            self.lat  = float(centroid.getElementsByTagName("latitude")[0].firstChild.nodeValue)
            self.placeType = dom.getElementsByTagName("placeTypeName")[0].firstChild.nodeValue
            self.placeTypeNum = int(dom.getElementsByTagName("placeTypeName")[0].getAttribute("code"))
            self.name = dom.getElementsByTagName("name")[0].firstChild.nodeValue
            sw = dom.getElementsByTagName("southWest")[0]
            swlong = float(sw.getElementsByTagName("longitude")[0].firstChild.nodeValue)
            swlat = float(sw.getElementsByTagName("latitude")[0].firstChild.nodeValue)
            ne = dom.getElementsByTagName("northEast")[0]
            nelong = float(ne.getElementsByTagName("longitude")[0].firstChild.nodeValue)
            nelat = float(ne.getElementsByTagName("latitude")[0].firstChild.nodeValue)
            self.box = [swlong, swlat, nelong, nelat]
        else:
            raise GeoPlanetError("NotFound")
        
    def is_in_bounding_box(self, long, lat):
        return long <= self.box[2] and \
               long >= self.box[0] and \
               lat <= self.box[3] and \
               lat >= self.box[1]

    def get_dist_between_points(self, long1, lat1, long2, lat2):
        degrees_to_radians = math.pi/180.0
        phi1 = (90.0 - lat1)*degrees_to_radians
        phi2 = (90.0 - lat2)*degrees_to_radians
        theta1 = long1*degrees_to_radians
        theta2 = long2*degrees_to_radians
        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
               math.cos(phi1)*math.cos(phi2))
        arc = math.acos( cos ) * 6373
        return arc

    def get_dist_from_place(self, place):
        return self.getDistBetweenPoints(self.long, self.lat,
                                         place.long, place.lat)
        
    def get_belong_tos(self):
	ret = []
        url = "%s%d/belongtos?%s" % (self.baseurl, self.woeid, self.baseparam)
        con = urllib.urlopen(url)
        data = con.read()
        con.close()
    	try:
            dom = parseString(data)
        except ExpatError:
            raise GeoPlanetError("Error while parsing response:" + data) 
        places = dom.getElementsByTagName("place")	
        for p in places:
            woeid = int(p.getElementsByTagName("woeid")[0].firstChild.nodeValue)
            placeType = p.getElementsByTagName("placeTypeName")[0].firstChild.nodeValue
            placeTypeNum = int(p.getElementsByTagName("placeTypeName")[0].getAttribute("code"))
            ret.append([woeid, placeType, placeTypeNum])
	return ret


class YahooGeoServices(YahooServices):

    timedout = False

    #gets all the places in the given text. The return results is a list of woeId, long, lat rows.
    def get_places(self, str, docType="text/plain"):
        url = "http://wherein.yahooapis.com/v1/document"
        params = urllib.urlencode({"appid":self.appId, 
                                   "documentContent" :str,
                                   "documentType":docType, 
                                   "outputType": "xml",
                                   "autoDisambiguate":"true"})
        con = urllib.urlopen(url, params)
        data = con.read()
        con.close()
        dom = parseString(data)
        places = dom.getElementsByTagName("place")
        ret = []
        for i in places:
            woeid = int(i.getElementsByTagName("woeId")[0].firstChild.nodeValue)
            lat = float(i.getElementsByTagName("latitude")[0].firstChild.nodeValue)
            long = float(i.getElementsByTagName("longitude")[0].firstChild.nodeValue)
            ret.append([woeid, long, lat])
        return ret

    #Returns the most granular place associated with the given long, lat. (does not work with sea/oceans)
    def reverse_geocode(self, long, lat):
	microform = '<div class="geo"><span class="latitude">%f</span>, <span class="longitude">%f</span></div>' % (lat, long)
	return self.get_places(microform, 'text/html')

    #Geocodes the string and returns the most probable place associated to it.
    def geocode(self, str):
        try:
            url = "http://where.yahooapis.com/v1/places.q(%s)?appid=%s&format=xml" % (urllib.quote(str), self.appId)
            con = urllib.urlopen(url)
            data = con.read()
            con.close()
            dom = parseString(data)
            if dom.getElementsByTagName("woeid"):
                result = []
                for woeidNode in dom.getElementsByTagName("woeid"):
                    woeid = woeidNode.firstChild.nodeValue
                    result.append(GeoPlanetPlace(woeid, self.appId))
                return result
            else:
                raise GeoPlanetError("Place Not Found:'%s'" % (str))
        except ExpatError:
            raise GeoPlanetError("Error") 
        except socket.error:
            print>>sys.stderr, "GOT SOCKET ERROR:" + errstr
            errno, errstr = sys.exc_info()[:2]
            if errno == socket.timeout and not self.timedout:       
                self.timedout = True
                return self.geocode(str)
            raise GeoPlanetError("Place Not Found:'%s'" % (str))
                



class GeoPlanetError:
    
    def __init__(self, msg):
        self.msg = msg

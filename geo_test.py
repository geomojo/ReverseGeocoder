import yahoogeoservices

geo = yahoogeoservices.YahooGeoServices('YOUR_APP_ID')
londons = geo.geocode('london, uk')
for place in londons:
    print "%s: %d" % (place.name, place.woeid)
    belongs = place.get_belong_tos()
    for woeid, placeType, placeTypeNum in belongs:
        print "belongsto: %d\t%s\t%d" % (woeid, placeType, placeTypeNum)

reversed = geo.reverse_geocode(-0.12714, 51.50632)
for place in reversed:
    print place[0]


text = "London is much better town than Paris but the best town in the World is New York"
places = geo.get_places(text)
for p in places:
    place = yahoogeoservices.GeoPlanetPlace(p[0], 'YOUR_APP_ID')
    print "%s: %d" % (place.name, place.woeid)

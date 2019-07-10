from googlesearch import search
import re
import socket
import requests
import collections

def get_locations(query, numResults):
    results = []
    pattern = re.compile('//(.*?)/')
    coordinates = []

    for result in search(query, stop=numResults, pause=2):
        results.append(result)
        #print(result)
        substring = pattern.search(result)
        clean_result = result[ (substring.span()[0]+2) : (substring.span()[1] - 1) ]
        #print(clean_result)
        ip = socket.gethostbyname(clean_result)
        #print(ip)
        r = requests.get(url = 'https://extreme-ip-lookup.com/json/' + ip)
        coordinates.append( (r.json()['lat'], r.json()['lon']))
        #coordinates.append( { "lat": r.json()['lat'], "lon": r.json()['lon'] } )
        #print(r.json()['lat'], r.json()['lon'])

    countedCoordinates = collections.Counter(coordinates)
    coordinates = list(countedCoordinates.keys())
    counts = list(countedCoordinates.values())

    return coordinates, counts

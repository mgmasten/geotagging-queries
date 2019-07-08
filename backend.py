from googlesearch import search
import re
import socket
import requests

def get_locations(query):
    results = []

    for result in search(query, stop=20, pause=2):
        results.append(result)

    results = list(set(results)) # Remove duplicates

    pattern = re.compile('//(.*?)/')
    coordinates = []
    for url in results:
        substring = pattern.search(url)
        clean_result = url[ (substring.span()[0]+2) : (substring.span()[1] - 1) ]
        ip = socket.gethostbyname(clean_result)
        r = requests.get(url = 'https://extreme-ip-lookup.com/json/' + ip)
        coordinates.append( { "lat": r.json()['lat'], "lon": r.json()['lon'] } )

    return coordinates

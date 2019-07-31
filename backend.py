from googlesearch import search
import re
import socket
import requests
import collections


def get_locations(query, numResults, searchOptions):
    coordinates = []
    pattern = re.compile('//(.*?)/')  # Create pattern to capture domain

    extra_params = {'lr': searchOptions.get('resultLanguage'),
                    'cr': searchOptions.get('resultCountry'),
                    'gl': searchOptions.get('searchCountry'),
                    'filter': searchOptions.get('filter'),
                    'cookies': searchOptions.get('cookies')}

    lang = searchOptions.get('searchLanguage')
    if lang is None:
        lang = 'en'

    safe = searchOptions.get('safe')

    for result in search(query, lang=lang, stop=numResults, pause=2, safe=safe, extra_params=extra_params):
        substring = pattern.search(result)
        clean_result = result[(substring.span()[0]+2): (substring.span()[1] - 1)]
        ip = socket.gethostbyname(clean_result)
        r = requests.get(url='https://extreme-ip-lookup.com/json/' + ip)
        coordinates.append((r.json()['lat'], r.json()['lon']))

    countedCoordinates = collections.Counter(coordinates)  # Count number of results at each location
    coordinates = list(countedCoordinates.keys())
    counts = list(countedCoordinates.values())

    return coordinates, counts

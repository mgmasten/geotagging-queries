from googlesearch import search
import re
import socket
import requests
from collections import Counter, defaultdict


def get_locations(query, numResults, searchOptions):
    coordinates = []
    results = []
    ret = []
    pattern = re.compile('//(.*?)/')  # Create pattern to capture domain

    extra_params = {'lr': searchOptions.get('resultLanguage'),
                    'cr': searchOptions.get('resultCountry'),
                    'gl': searchOptions.get('searchCountry'),
                    'filter': searchOptions.get('filter')}

    lang = searchOptions.get('searchLanguage')
    if lang is None:
        lang = 'en'

    safe = searchOptions.get('safe')

    for result in search(query, lang=lang, stop=numResults, pause=2, cookies=False, safe=safe, extra_params=extra_params):
        substring = pattern.search(result)
        clean_result = result[(substring.span()[0]+2): (substring.span()[1] - 1)]
        ip = socket.gethostbyname(clean_result)
        r = requests.get(url='https://extreme-ip-lookup.com/json/' + ip)
        coordinate = (r.json()['lat'], r.json()['lon'])
        coordinates.append(coordinate)
        ret.append((coordinate, result))
    #print(results)
    #print(coordinates)

    # countedCoordinates = Counter(coordinates)  # Count number of results at each location
    # coordinates = list(countedCoordinates.keys())
    # counts = list(countedCoordinates.values())

    d = defaultdict(list)
    for k, *v in ret:
        d[k].append(v)

    d = tuple(d.items())
    return [i[0] for i in d], [len(i[1]) for i in d], [i[1] for i in d]

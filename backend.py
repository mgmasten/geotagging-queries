from googlesearch2 import search
import re
import socket
import requests
from collections import Counter, defaultdict


def get_locations(query, numResults, searchOptions):
    coordinates = []
    results = []
    ret = []
    pattern = re.compile('//(.*?)/')  # Create pattern to capture domain

    extra_params = {'lr': searchOptions['resultLanguage'],
                    'cr': searchOptions['resultCountry'],
                    'gl': searchOptions['searchCountry'],
                    'filter': searchOptions['filter']}

    lang = searchOptions['searchLanguage']

    tbs = searchOptions['dateRestrict']
    if tbs == 'qdr:d':
        tbs = '0'

    domains = searchOptions['domains']
    if domains:
        domains = domains.split()

    domainAction = searchOptions['domainAction']

    safe = searchOptions['safe']
    tpe = searchOptions['resultType']

    for result in search(query, lang=lang, tbs=tbs, safe=safe, cookies=False, stop=numResults, domains=domains, domainAction=domainAction, pause=2, extra_params=extra_params, tpe=tpe):
        substring = pattern.search(result[0])  # Search for pattern in url
        name = result[1]  # Grab the name that Google displays
        clean_result = result[0][(substring.span()[0]+2): (substring.span()[1] - 1)]
        ip = socket.gethostbyname(clean_result)
        r = requests.get(url='https://extreme-ip-lookup.com/json/' + ip)
        coordinate = (r.json()['lat'], r.json()['lon'])
        coordinates.append(coordinate)
        ret.append((coordinate, result[0], name, clean_result))
    #print(results)
    #print(coordinates)
    # countedCoordinates = Counter(coordinates)  # Count number of results at each location
    # coordinates = list(countedCoordinates.keys())
    # counts = list(countedCoordinates.values())

    d = defaultdict(list)
    for k, *v in ret:
        d[k].append((v[0], v[1], v[2]))

    d = tuple(d.items())
    return [i[0] for i in d], [len(i[1]) for i in d], [i[1] for i in d]

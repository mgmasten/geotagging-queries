import re
import socket
import requests
import csv
from collections import Counter, defaultdict, OrderedDict

from googlesearch2 import search
from googletrans import Translator

import extractLocation

cities_dict = {}
languages_dict = {}
tlds_dict = {}
postalcode_dict = {}

supported_countries = {'us', 'ca', 'au', 'my'}

def ip_geolocate(domain):
    ip = socket.gethostbyname(domain)
    try:
        r = requests.get(url='https://extreme-ip-lookup.com/json/' + ip)
    except:
        return None
    coordinate = (r.json()['lat'], r.json()['lon'])
    return coordinate

# Reformat a list of results tuples (coordinate, url, name, domain) so it is
# organized by coordinate, with lists of the associated (url, name, domain) tuples
def reformat_results(results):
    d = defaultdict(list)
    for k, *v in results:
        d[k].append((v[0], v[1], v[2]))

    d = tuple(d.items())
    return {'locations': [i[0] for i in d], 'frequencies': [len(i[1]) for i in d], 'urls': [i[1] for i in d]}


# Takes in a query and all related parameters and returns a list of the results
# Results are organized by coordinate, and include url, name (as displayed on Google), and domain
# if ipAddress is True, the IP address method is used for geolocation
# if scraping is True, the scraping method is used for geolocation
def get_locations(query, numResults, ipAddress, scraping, searchOptions):
    create_languages_and_tlds_dict()
    create_postalcode_dict()

    ip_results = []
    ip_coordinates = []

    scraping_results = []
    scraping_coordinates = []

    domain_pattern = re.compile('//(.*?)/')  # Regular expression to capture domain part of url
    tld_pattern = re.compile('\.[^\.]*$')    # Regular expression to capture tld
    site_name_pattern = re.compile('[^\.]*.') # Regular expression to capture site name

    # Get extra_params into form accepted by googlesearch's search function
    extra_params = {'lr': searchOptions['resultLanguage'],
                    'cr': searchOptions['resultCountry'],
                    'gl': searchOptions['searchCountry'],
                    'filter': searchOptions['filter']}

    search_lang = searchOptions['searchLanguage']

    tbs = searchOptions['dateRestrict']
    if tbs == 'qdr:d':  # If date restrict was not set, set it to 0 ('d' means 1 day)
        tbs = '0'

    domains = searchOptions['domains']
    if domains: # If multiple domains were given separated by spaces, split them
        domains = domains.split()
    domainAction = searchOptions['domainAction']

    safe = searchOptions['safe']
    tpe = searchOptions['resultType']

    # Set up a googletrans Translator
    translator = Translator()

    # Get the results (urls and names) from googlesearch's search function
    results = search(query, lang=search_lang, tbs=tbs, safe=safe, cookies=False, stop=numResults, domains=domains, domainAction=domainAction, pause=2, extra_params=extra_params, tpe=tpe)
    if results:
        for result in results:
            url = result[0]
            name = result[1]  # Get the name that Google displays

            # Extract domain
            substring = domain_pattern.search(url)
            domain = url[(substring.span()[0]+2): (substring.span()[1] - 1)]

            if ipAddress == 'true':
                coordinate = ip_geolocate(domain)
                ip_coordinates.append(coordinate)
                return_name = lambda x : x if x else 'No name'
                ip_results.append((coordinate, result[0], return_name(name), domain))

            if scraping == 'true':
                # Extract tld and get the associated country
                substring = tld_pattern.search(domain)
                tld = domain[substring.span()[0]:substring.span()[1]]
                tld_country = tlds_dict.get(tld)

                # Extract website name
                substring = site_name_pattern.search(domain)
                website_name = domain[substring.span()[0]:(substring.span()[1] - 1)]

                # Detect language of name and website name
                detect1 = None
                detect2 = None
                if name is not None:
                    return_name = name
                    try:
                        # One common reason this fails is because the names can include html
                        detect1 = translator.detect(name)
                    except:
                        pass
                else:
                    return_name = 'No name'

                try:
                    detect2 = translator.detect(website_name)
                except:
                    pass

                languages = set()  # Language guesses for page
                language_countries = set()  # Country guesses for page

                # If a resultLanguage was set, add it and all countries it is spoken in as guesses
                if searchOptions['resultLanguage']:
                    languages = languages | set(searchOptions['resultLanguage'][5:len(searchOptions['resultLanguage'])-1])
                    langs = [languages_dict.get(x) for x in searchOptions['resultLanguage']]
                    if langs:
                        language_countries = language_countries | set(langs)

                # If a searchLanguage was set, add it as a language guess
                if search_lang:
                    languages.add(search_lang)

                # If there is a high confidence in the name and website_name language detections,
                # add them and the countries they are spoken in as guesses
                if detect1 and detect1.confidence > 0.75:
                    languages.add(detect1.lang)
                    langs = languages_dict.get(detect1.lang)
                    if langs:
                        language_countries = language_countries | set(langs)
                if detect2 and detect2.confidence > 0.75:
                    languages.add(detect2.lang)
                    langs = languages_dict.get(detect2.lang)
                    if langs:
                        language_countries = language_countries | set(langs)

                country_guesses = OrderedDict()  # Ordered dict so that countries put in first have highest priority

                # If resultCountry was set, add them as the FIRST country guesses
                if searchOptions['resultCountry']:
                    for country in [x[7:9].lower() for x in searchOptions['resultCountry']]:
                        if country_guesses.get(country) is None:
                            country_guesses[country] = country

                # If searchCountry was set, add it as a guess SECOND
                if searchOptions['searchCountry'] and country_guesses.get(searchOptions['searchCountry']) is None:
                    country_guesses[searchOptions['searchCountry']] = searchOptions['searchCountry']

                # Add tld country as a THIRD guess
                if tld_country and country_guesses.get(tld_country) is None:
                    country_guesses[tld_country] = tld_country

                # Then add the countries associated with the languages
                if language_countries:
                    for country in language_countries:
                        if country_guesses.get(country) is None:
                            country_guesses[country] = country

                # Add the US, if it wasn't already in the list
                if country_guesses.get('us') is None:
                    country_guesses['us'] = 'us'

                coordinate = extractLocation.extract_location_from_site(url, languages, country_guesses)
                scraping_coordinates.append(coordinate)
                scraping_results.append((coordinate, url, return_name, domain))

    if ip_results:
        ip_results = reformat_results(ip_results)

    if scraping_results:
        scraping_results = reformat_results(scraping_results)

    return {'ip': ip_results, 'scraping': scraping_results}

# Create two dictionaries.
# languages_dict maps a language code onto the countries in which it is spoken
# tlds_dict maps a top-level domain onto the associated country
def create_languages_and_tlds_dict():
    with open('./location-data/country-info.txt', mode='r', newline='') as languages_file:
        reader = csv.reader(languages_file, delimiter='\t')
        next(reader)  # Skip headers
        for row in reader:
            country = row[0].lower()
            languages = row[15].split(',')
            tld = row[9].lower()

            for language in languages:
                if languages_dict.get(language):
                    languages_dict[language].append(country)
                else:
                    languages_dict[language] = [country]

            tlds_dict[tld] = country

# Creates a dict that maps a country and postalcode onto a lat/lon coordinate
def create_postalcode_dict():
    for country in supported_countries:
        postalcode_dict[country] = {}
        file_location = './location-data/postalcodes/' + country.upper() + '.txt'
        with open(file_location, mode='r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                postalcode_dict[country][row[1]] = (row[9], row[10])

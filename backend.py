from googlesearch2 import search
import re
import socket
import requests
from collections import Counter, defaultdict, OrderedDict
import csv
from googletrans import Translator
import database
import extractLocation

cities_dict = {}
max_words_city_name = 14
languages_dict = {}
tlds_dict = {}
iso2_to_name = {}
iso3_to_name = {}
name_to_isos = {}
iso2_to_postal = {}
regex_dict = {}
postalcode_dict = {}

supported_countries = {'us', 'ca', 'au', 'my'}

def get_locations(query, numResults, ipAddress, scraping, searchOptions):
    ip_results = []
    scraping_results = []
    ip_coordinates = []
    scraping_coordinates = []
    domain_pattern = re.compile('//(.*?)/')  # Create pattern to capture domain
    tld_pattern = re.compile('\.[^\.]*$')
    site_name_pattern = re.compile('[^\.]*.')

    extra_params = {'lr': searchOptions['resultLanguage'],
                    'cr': searchOptions['resultCountry'],
                    'gl': searchOptions['searchCountry'],
                    'filter': searchOptions['filter']}

    search_lang = searchOptions['searchLanguage']

    tbs = searchOptions['dateRestrict']
    if tbs == 'qdr:d':
        tbs = '0'

    domains = searchOptions['domains']
    if domains:
        domains = domains.split()

    domainAction = searchOptions['domainAction']

    safe = searchOptions['safe']
    tpe = searchOptions['resultType']

    translator = Translator()

    for result in search(query, lang=search_lang, tbs=tbs, safe=safe, cookies=False, stop=numResults, domains=domains, domainAction=domainAction, pause=2, extra_params=extra_params, tpe=tpe):
        url = result[0]
        name = result[1]  # Grab the name that Google displays
        substring = domain_pattern.search(url)  # Search for pattern in url

        domain = url[(substring.span()[0]+2): (substring.span()[1] - 1)]
        if ipAddress == 'true':
            ip = socket.gethostbyname(domain)
            r = requests.get(url='https://extreme-ip-lookup.com/json/' + ip)
            coordinate = (r.json()['lat'], r.json()['lon'])
            ip_coordinates.append(coordinate)
            if name is None:
                return_name = 'No name'
            else:
                return_name = name
            ip_results.append((coordinate, result[0], return_name, domain))

        if scraping == 'true':
            substring = tld_pattern.search(domain)
            tld = domain[substring.span()[0]:substring.span()[1]]
            tld_country = tlds_dict.get(tld)

            substring = site_name_pattern.search(domain)
            website_name = domain[substring.span()[0]:(substring.span()[1] - 1)]

            if name is not None:
                detect1 = translator.detect(name)
                return_name = name
            else:
                return_name = 'No name'
            detect2 = translator.detect(website_name)

            languages = set()
            language_countries = set()
            if searchOptions['resultLanguage']:
                languages = languages | set(searchOptions['resultLanguage'][5:len(searchOptions['resultLanguage'])-1])
                langs = [languages_dict.get(x) for x in searchOptions['resultLanguage']]
                if langs:
                    language_countries = language_countries | set(langs)
            if search_lang:
                languages.add(search_lang)
            # Exclude languages that are spoken in many countries?
            if detect1 and detect1.confidence > 0.75:
                languages.add(detect1.lang)
                langs = languages_dict.get(detect1.lang)
                if langs:
                    language_countries = language_countries | set(langs)
            if detect2.confidence > 0.75:
                languages.add(detect2.lang)
                langs = languages_dict.get(detect2.lang)
                if langs:
                    language_countries = language_countries | set(langs)

            country_guesses = OrderedDict()
            if searchOptions['resultCountry']:
                for country in [x[7:9].lower() for x in searchOptions['resultCountry']]:
                    if country_guesses.get(country) is None:
                        country_guesses[country] = country
            if searchOptions['searchCountry'] and country_guesses.get(searchOptions['searchCountry']) is None:
                country_guesses[searchOptions['searchCountry']] = searchOptions['searchCountry']
            if tld_country and country_guesses.get(tld_country) is None:
                country_guesses[tld_country] = tld_country
            if language_countries:
                for country in language_countries:
                    if country_guesses.get(country) is None:
                        country_guesses[country] = country

            if country_guesses.get('us') is None:
                country_guesses['us'] = 'us'

            coordinate = extractLocation.extract_owner_location(url, languages, country_guesses)
            scraping_coordinates.append(coordinate)
            scraping_results.append((coordinate, url, return_name, domain))
        # if new_coordinate:
        #     # print('Found location ', lat, lon, ' for ', name)
        #     ret2.append((coordinate, result[0], name, clean_result))

    #print(ret2)
    #print(results)
    #print(coordinates)
    # countedCoordinates = Counter(coordinates)  # Count number of results at each location
    # coordinates = list(countedCoordinates.keys())
    # counts = list(countedCoordinates.values())

    if ip_results:
        d = defaultdict(list)
        for k, *v in ip_results:
            d[k].append((v[0], v[1], v[2]))

        d = tuple(d.items())
        ip_results = {'locations': [i[0] for i in d], 'frequencies': [len(i[1]) for i in d], 'urls': [i[1] for i in d]}

    if scraping_results:
        d = defaultdict(list)
        for k, *v in scraping_results:
            d[k].append((v[0], v[1], v[2]))

        d = tuple(d.items())
        scraping_results = {'locations': [i[0] for i in d], 'frequencies': [len(i[1]) for i in d], 'urls': [i[1] for i in d]}

    return {'ip': ip_results, 'scraping': scraping_results}

# def create_cities_dictionary():
    # lat_lon_tolerance = 10
    #
    # def same_coordinates(coords1, coords2):
    #     return (abs(coords1[0] - coords2[0]) < lat_lon_tolerance) and (abs(coords1[1] - coords2[1]) < lat_lon_tolerance)
    #
    # def coordinates_exist(old_entries, new_coords):
    #     for entry in old_entries:
    #         if same_coordinates(entry, new_coords):
    #             return True
    #     return False
    #
    # with open('./world-cities-database/worldcitiespop.csv', mode='r', newline='') as locations_file:
    #     reader = csv.reader(locations_file, delimiter=',')
    #     next(reader) # Skip headers on first line
    #     for row in reader:
    #         country = row[0]
    #         if country == 'zr': # Zaire was renamed to Democratic Republic of the Congo
    #             country = 'cd'  # This dataset has entries for both names
    #         city = row[1]
    #         lat = float(row[5])
    #         lon = float(row[6])
    #         previous_entries = cities_dict.get(city)
    #         if previous_entries:
    #             matching_country_entries = previous_entries.get(country)
    #             if matching_country_entries:
    #                 if coordinates_exist(matching_country_entries, (lat, lon)):
    #                     continue
    #                 else:
    #                     cities_dict[city][country].append((lat, lon))
    #             else:
    #                 cities_dict[city][country] = [(lat, lon)]
    #         else:
    #             cities_dict[city] = {country: [(lat, lon)]}  # Country, lat, lon

def create_languages_and_tlds_dict():
    with open('./location-data/country-info.txt', mode='r', newline='') as languages_file:
        reader = csv.reader(languages_file, delimiter='\t')
        next(reader)  #Skip headers
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

def create_country_dicts():
    with open('./location-data/country-info.txt', mode='r') as countries_info:
        reader = csv.reader(countries_info, delimiter='\t')
        next(reader)  # Skip headers on first line

        for row in reader:
            iso2 = row[0]
            iso3 = row[1]
            country_name = row[4]
            tld = row[9]
            #print(iso2)
            postal_code_format = row[13]
            postal_code_regex = row[14]
            languages = row[15]
            geoname_id = row[16]

            iso2_to_name[iso2] = country_name
            iso3_to_name[iso3] = country_name
            name_to_isos[country_name] = {'iso2': iso2, 'iso3': iso3}
            iso2_to_postal[iso2] = {'format': postal_code_format, 'regex': postal_code_regex}

def create_regex_dict():
    with open('./location-data/postal-code-regex.txt', mode='r') as regex_info:
        reader = csv.reader(regex_info, delimiter='\t')

        for row in reader:
            if row[0]:
                regex_dict[row[0]] = row[1]

def create_postalcode_dict():
    for country in supported_countries:
        postalcode_dict[country] = {}
        file_location = './location-data/postalcodes/' + country.upper() + '.txt'
        with open(file_location, mode='r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                postalcode_dict[country][row[1]] = (row[9], row[10])

def create_cities_dictionary(filename, delimiter, country_index, isISO, lat_index, lon_index, lat_lon_tolerance=10, city_index=None, alternate_names_index=None):
    def same_coordinates(coords1, coords2):
        return (abs(coords1[0] - coords2[0]) < lat_lon_tolerance) and (abs(coords1[1] - coords2[1]) < lat_lon_tolerance)

    def coordinates_exist(old_entries, new_coords):
        for entry in old_entries:
            if same_coordinates(entry, new_coords):
                return True
        return False

    with open(filename, mode='r', newline='') as locations_file:
        reader = csv.reader(locations_file, delimiter=delimiter)
        for row in reader:
            country = row[country_index]
            if country == 'zr':  # Zaire was renamed to Democratic Republic of the Congo
                country = 'cd'   # This dataset has entries for both names

            if alternate_names_index: # Assumes comma-separated, same string
                city = row[alternate_names_index].split(',')
                # Correct for missing tabs in allCountries.txt
                try:
                    lat = float(city[len(city) - 1])
                    lon = float(row[alternate_names_index + 1])
                    del city[len(city) - 1]
                except:
                    lat = float(row[lat_index])
                    lon = float(row[lon_index])
            else:
                city = [row[city_index]]
                lat = float(row[lat_index])
                lon = float(row[lon_index])

            for city_name in city:
                previous_entries = cities_dict.get(city_name)
                if previous_entries:
                    matching_country_entries = previous_entries.get(country)
                    if matching_country_entries:
                        if coordinates_exist(matching_country_entries, (lat, lon)):
                            continue
                        else:
                            cities_dict[city_name][country].append((lat, lon))
                    else:
                        cities_dict[city_name][country] = [(lat, lon)]
                else:
                    cities_dict[city_name] = {country: [(lat, lon)]}  # Country, lat, lon

def city_search(name, result_country, search_country, tld_country, language_countries):
    database_file = "./pythonsqlite.db"
    conn = database.create_connection(database_file)

    if conn is None:
        print("Error! cannot create the database connection.")
        return

    results = {}
    country = None
    # Filter out bold tags
    open = name.find('<b>')
    close = name.find('</b>')
    name = name[0:open] + name[open+3:close] + name[close+4:len(name)]

    name_words = name.split(' ')

    for start in range(0, len(name_words)):
        for end in range(start + 1, len(name_words) + 1):
            if (end-start > max_words_city_name):
                continue
            city = ' '.join(name_words[start:end])
            # record = cities_dict.get(city)
            records = database.find_city(conn, city)
            if records:
                print('Name:', name_words[start:end])
                print('Records:', records)
                if results.get(len(city)):
                    results[len(city)].append(records)
                else:
                    results[len(city)] = [records]
            if name_to_isos.get(city): # This is a country, need to consider language
                country = name_to_isos[city][iso2]

    city_words = max_words_city_name
    best_guess = None

    while(city_words > 0):
        if results.get(city_words):
            for record in results[city_words]:
                if country and record.get(country):
                    print('A+ guess:', record[country]) # Need to consider language
                    return record[country]
                elif result_country and record.get(result_country):
                    print('A+ guess:', record[result_country])
                    return record[result_country]
                elif tld_country and record.get(tld_country):
                    print('A guess:', record[tld_country])
                    return record[tld_country]
                elif search_country and record.get(search_country):
                    print('B guess:', record[search_country])
                    return record[search_country]
                elif language_countries:
                    entries = [record.get(country) for country in language_countries]
                    for entry in entries:
                        if entry is not None and best_guess is None:
                            best_guess = entry

            city_words -= 1

    return best_guess

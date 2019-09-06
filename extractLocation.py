from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import requests
from googletrans import Translator
from difflib import SequenceMatcher
import urllib.parse
import backend


us_region_codes = {'al', 'ak', 'as', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'dc',
    'fl', 'ga', 'gu', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me',
    'md', 'mh', 'ma', 'mi', 'fm', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh',
    'nj', 'nm', 'ny', 'nc', 'nd', 'mp', 'oh', 'ok', 'or', 'pw', 'pa', 'pr',
    'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'vi', 'wa', 'wv', 'wi', 'wy'}

us_region_names = {'alabama', 'alaska', 'american samoa', 'arizona', 'arkansas', 'california', 'colorado',
    'connecticut', 'delaware', 'washington d.c.', 'washington dc', 'florida', 'georgia', 'guam', 'hawaii', 'idaho', 'illinois',
    'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'marshall islands'
    'massachusetts', 'michigan', 'micronesia', 'minnesota', 'mississippi', 'missouri', 'montana',
    'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico', 'new york',
    'north carolina', 'north dakota', 'northern mariana islands', 'ohio', 'oklahoma', 'oregon', 'palau', 'pennsylvania',
    'puerto rico', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah',
    'vermont', 'virginia', 'virgin islands', 'us virgin islands', 'u.s. virgin islands', 'washington', 'west virginia', 'wisconsin', 'wyoming'}

ca_region_codes = {'ab', 'bc', 'mb', 'nb', 'nl', 'nt', 'ns', 'nu', 'on', 'pe', 'qc', 'sk', 'yt'}

ca_region_names = {'alberta', 'british columbia', 'manitoba', 'new brunswick', 'newfoundland and labrador', 'newfoundland', 'labrador',
                    'nova scotia', 'ontario', 'prince edward island', 'quebec', 'saskatchewan', 'northwest territories', 'nunavut', 'yukon'}

au_region_codes = {'act', 'nsw', 'nt', 'qld', 'sa', 'tas', 'vic', 'wa'}

au_region_names = {'new south wales', 'queensland', 'south australia', 'tasmania', 'victoria', 'western australia', 'australian capital territory',
                    'jervis bay territory', 'northern territory', 'ashmore and cartier islands', 'coral sea islands'}

my_region_names = {'penang', 'selangor', 'johor', 'sabah', 'sarawak', 'perak', 'kedah', 'pahang', 'kelantan', 'malacca', 'terengganu', 'negeri sembilan', 'perlis',
                    'kuala lumpur', 'labuan', 'putrajaya'}

url_pattern = re.compile('(.*//)(.*?/)')

# Format: (regex, postalcode_index, [(capturing_group, valid_options), ...])
regex_dict = {'us': [('([A-Z]{2})/s?(\d{5})([ \-]\d{4})?', 1, [(0, us_region_codes)]),
                     ('([A-Za-z]\.?[A-Za-z]\.?\s)(\d{5})([ \-]\d{4})?', 1, [(0, us_region_codes)]),
                     ('(,?[a-zA-Z ]{1,17}\s?)(\d{5})([ \-]\d{4})?', 1, [(0, us_region_names)])],
              'ca': [('(,?[A-Z]{2})\s?([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJ-NPRSTV-Z])\s?(\d[ABCEGHJ-NPRSTV-Z]\d)', 1, [(0, ca_region_codes)]),
                     ('(,?[a-zA-Z]\.?[a-zA-Z]\.?)\s?([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJ-NPRSTV-Z])\s?(\d[ABCEGHJ-NPRSTV-Z]\d)', 1, [(0, ca_region_codes)]),
                     ('(,?[a-zA-Z ]{1,20})\s?([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJ-NPRSTV-Z]\s?\d[ABCEGHJ-NPRSTV-Z]\d)', 1, [(0, ca_region_names)])],
              'au': [('([A-Z]{2,3})\s?(\d{4})', 1, [(0, au_region_codes)]),
                    ('([A-Za-z]{2,3})\s?(\d{4})', 1, [(0, au_region_codes)]),
                    ('(,?[a-zA-Z ]{1,30}),?\s?(\d{4})', 1, [(0, au_region_names)])],
              'my': [('(\d{5})[a-zA-Z ]{1,20}\s([a-zA-Z]{5,11}([ ][a-zA-Z]{6,10})?)', 0, [(1, my_region_names)])]
}

nominatim_countries = {'us'}

translator = Translator()

def extractName(a):
    # a is the string of the full anchor HTML tag
    # Returns the text displayed for the link

    start = a.find('>')
    end = a.find('</a>')
    name = a[start+1:end]

    if '<img' in name: # Clickable image, not text
        return None
    else:
        return name


def try_regex(webpage_text, pattern):
    return re.findall(pattern, webpage_text)
    # substring = pattern.search(webpage_text)
    # if substring:
    #     #print(webpage_text[substring.span()[0]:substring.span()[1]])
    #     split_string = pattern.search(webpage_text).groups()
    #     print(split_string)
    #     return split_string
    #
    # else:
    #     return []

        # state_and_postalcode = text[substring.span()[0]:(substring.span()[1])]
        # print(split_string)
        # if split_string[0]:
        #     region = re.sub('\.|\ ', '', split_string[0])
        # if split_string[1]:
        #     postalcode = split_string[1]
        # if len(split_string) > 2 and split_string[2]:
        #     postalcode += split_string[2]


def find_location_from_page(webpage_text, country_guesses):
        for country in [x[0] for x in country_guesses.items()]:
            if country in backend.supported_countries:
                print(country)
                for regex_entry in regex_dict[country]:
                    #print(regex_entry)
                    pattern = re.compile(regex_entry[0])
                    results = try_regex(webpage_text, pattern)

                    if results:
                        for result in results:
                            #print(result)
                            #english_result = [x.text for x in translator.translate(result, dest='en')]
                            english_result = result
                            valid = True
                            for restriction in regex_entry[2]:
                                print(re.sub(',|\.', '', english_result[restriction[0]].lower().strip()))
                                text = re.sub(',|\.', '', english_result[restriction[0]].lower().strip())
                                if text not in restriction[1]:
                                    print('Not valid')
                                    valid = False
                                    break

                            if valid:
                                postalcode = re.sub(',|\.|\ ', '', result[regex_entry[1]])
                                # if country in nominatim_countries:
                                #     nominatim_url = 'https://nominatim.openstreetmap.org/search?format=json&country=' + country.upper() + '&postalcode=' + postalcode
                                #     nominatim_response = requests.get(nominatim_url)
                                #     if nominatim_response.json():
                                #         return (nominatim_response.json()[0]['lat'], nominatim_response.json()[0]['lon'])
                                # elif country == 'ca':
                                    #return backend.postalcode_dict[country][postalcode]
                                location = backend.postalcode_dict[country].get(postalcode)
                                if location:
                                    return location

        return None

def generate_contact_translations(page_languages):
    ret_translations = {'contact'}
    for page_language in page_languages:
        translations = translator.translate(['contact', 'contact us', 'contact them', 'contact information', 'contact page', 'I want contact', 'there was contact'], src='en', dest=page_language)
        ret_translations.add(translations[0].text.lower())
        contact_us = translations[1].text.lower()
        contact_them = translations[2].text.lower()
        contact_info = translations[3].text.lower()
        contact_page = translations[4].text.lower()
        I_want_contact = translations[5].text.lower()
        there_was_contact = translations[6].text.lower()

        start1, start2, length = SequenceMatcher(None, contact_us, contact_them).find_longest_match(0, len(contact_us), 0, len(contact_them))
        if length > 0:
            contact_verb = contact_us[start1:start1+length].strip()
            ret_translations.add(contact_verb)

        start1, start2, length = SequenceMatcher(None, contact_info, contact_page).find_longest_match(0, len(contact_info), 0, len(contact_page))
        if length > 0:
            contact_adjective = contact_info[start1:start1+length].strip()
            ret_translations.add(contact_verb)

        start1, start2, length = SequenceMatcher(None, I_want_contact, there_was_contact).find_longest_match(0, len(I_want_contact), 0, len(there_was_contact))
        if length > 0:
            contact_noun = I_want_contact[start1:start1+length].strip()
            ret_translations.add(contact_verb)

    return ret_translations

# url = 'https://catholicmasstime.org/church/our-lady-of-lavang/15698/'
def extract_owner_location(url, languages, country_guesses):
    print('URL: ', url)
    location = None

    user_agent = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)'
    request = Request(url)
    request.add_header('User-Agent', user_agent)
    response = urlopen(request)
    html = response.read()
    response.close()

    soup = BeautifulSoup(html, 'html.parser')
    page_text = soup.get_text()

    split_url = url_pattern.search(url).groups()
    url_prefix = split_url[0]
    url_root = split_url[0] + split_url[1]
    #print('Prefix: ' + url_prefix)
    #print('Root: ' + url_root)

    contact_translations = generate_contact_translations(languages)

    # Try to find a "contact" page
    for link in soup.find_all('a'):
        name = extractName(str(link))
        if name and any([x in name.lower() for x in contact_translations]):
            # if '//' in link['href']:
            #     if link['href'][0:2] == '//':
            #         contact_url = url_prefix + link['href']
            #     else:  # Is absolute
            #         contact_url = link['href']
            # else:
            #     if link['href'][0:3] == 'www':
            #         contact_url = link['href']
            #     if link['href'][0] == '/': # Relative to root folder
            #         contact_url = url_root + link['href']
            #     elif link['href'][0] =='#': # This page
            #         contact_url = url + '/' + link['href']
            #     else:  # Relative to this page
            #         contact_url = url + '/' + link['href']
            print('Contact link name: ', name)
            contact_url = urllib.parse.urljoin(url_root, link['href'])

            print('link: ' + contact_url)

            contact_request = Request(contact_url)
            contact_request.add_header('User-Agent', user_agent)
            try:
                contact_response = urlopen(contact_request)
            except:
                print('Could not open url')
                continue
            contact_html = contact_response.read()
            contact_response.close()
            # contact_html = requests.get(contact_url)

            contact_soup = BeautifulSoup(contact_html, 'html.parser')
            contact_page_text = contact_soup.get_text()

            location = find_location_from_page(contact_page_text, country_guesses)
            if location:
                print(location)
                return location


    location = find_location_from_page(page_text, country_guesses)
    print(location)
    return location

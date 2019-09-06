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
                    'kuala lumpur', 'labuan', 'putrajaya', 'malaysia'}

url_pattern = re.compile('(.*//)(.*?/)') # Regex to separate out components of a url

# Format: (regex, postalcode_index, [(capturing_group, valid_options), ...])
# The regexes are gone through sequentially, and the idea is that the first one in the list is easiest/most common.
regex_dict = {'us': [('([A-Z]{2})/s?(\d{5})([ \-]\d{4})?', 1, [(0, us_region_codes)]),
                     ('([A-Za-z]\.?[A-Za-z]\.?\s)(\d{5})([ \-]\d{4})?', 1, [(0, us_region_codes)]),
                     ('(,?[a-zA-Z ]{1,17}\s?)(\d{5})([ \-]\d{4})?', 1, [(0, us_region_names)])],
              'ca': [('(,?[A-Z]{2})\s?([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJ-NPRSTV-Z])\s?(\d[ABCEGHJ-NPRSTV-Z]\d)', 1, [(0, ca_region_codes)]),
                     ('(,?[a-zA-Z]\.?[a-zA-Z]\.?)\s?([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJ-NPRSTV-Z])\s?(\d[ABCEGHJ-NPRSTV-Z]\d)', 1, [(0, ca_region_codes)]),
                     ('(,?[a-zA-Z ]{1,20})\s?([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJ-NPRSTV-Z]\s?\d[ABCEGHJ-NPRSTV-Z]\d)', 1, [(0, ca_region_names)])],
              'au': [('([A-Z]{2,3})\s?(\d{4})', 1, [(0, au_region_codes)]),
                    ('([A-Za-z]{2,3})\s?(\d{4})', 1, [(0, au_region_codes)]),
                    ('(,?[a-zA-Z ]{1,30}),?\s?(\d{4})', 1, [(0, au_region_names)])],
              'my': [('(\d{5})\s[a-zA-Z ]{1,20},?\s*([a-zA-Z]{5,11}([ ][a-zA-Z]{6,10})?)', 0, [(1, my_region_names)])]
}

# Create a googletrans Translator
translator = Translator()

# a is the string of the full anchor HTML tag
# Returns the text displayed for the link
def extractName(a):
    start = a.find('>')
    end = a.find('</a>')
    name = a[start+1:end]

    if '<img' in name: # Clickable image, not text
        return None
    else:
        return name

# Given the text of a webpage and a list of potential countries, try to find
# a postalcode using regexes for that country.
# Regexes were created by combining the following sources:
#       - Frank's Compulsive Guide to Postal Addresses (http://www.columbia.edu/~fdc/postal/)
#       - CLDR postalcode regexes (http://cldr.unicode.org/index/downloads). See also location-data/postalcodes/regex/CLDR_regex
#       - The geonames dataset (location-data/country-info.txt)

# Uses geonames dataset (location-data/postalcodes, see geonames_readme.txt) to assign a lat/lon to a postalcode
# Another option is https://nominatim.org/release-docs/develop/api/Search/, but coverage
# was less comprehensive so I switched to the geonames dataset
def find_location_from_page(webpage_text, country_guesses):
    for country in [x[0] for x in country_guesses.items()]:
        if country in backend.supported_countries:
            for regex_entry in regex_dict[country]:
                # Compile the regex and get all matches
                pattern = re.compile(regex_entry[0])
                results = re.findall(pattern, webpage_text)

                if results:
                    for result in results:
                        # Ideally would translate words into english for matching with region names
                        # Not currently working
                        # english_result = [x.text for x in translator.translate(result, dest='en')]
                        english_result = result
                        valid = True
                        # Make sure the text near the zipcode conforms to the restrictions (region names, etc)
                        for restriction in regex_entry[2]:
                            text = re.sub(',|\.|<br>|<b>|</b>|"', '', english_result[restriction[0]].lower().strip())
                            if text not in restriction[1]:
                                valid = False
                                break

                        if valid:
                            postalcode = re.sub(',|\.|\ ', '', result[regex_entry[1]])
                            location = backend.postalcode_dict[country].get(postalcode)
                            if location:
                                return location

    return None

# Generate many possible translations of the word "contact" into the candidate languages
# Try to find a noun, verb, and adjective version by finding the similar words between different sentences
def generate_contact_translations(page_languages):
    ret_translations = {'contact'}
    for page_language in page_languages:
        try:
            translations = translator.translate(['contact', 'contact us', 'contact them', 'contact information', 'contact page', 'I want contact', 'there was contact'], src='en', dest=page_language)
        except:
            return ret_translations

        ret_translations.add(translations[0].text.lower())
        contact_us = translations[1].text.lower()
        contact_them = translations[2].text.lower()
        contact_info = translations[3].text.lower()
        contact_page = translations[4].text.lower()
        I_want_contact = translations[5].text.lower()
        there_was_contact = translations[6].text.lower()

        # Find verb version
        start1, start2, length = SequenceMatcher(None, contact_us, contact_them).find_longest_match(0, len(contact_us), 0, len(contact_them))
        if length > 0:
            contact_verb = contact_us[start1:start1+length].strip()
            ret_translations.add(contact_verb)

        # Find adjective version
        start1, start2, length = SequenceMatcher(None, contact_info, contact_page).find_longest_match(0, len(contact_info), 0, len(contact_page))
        if length > 0:
            contact_adjective = contact_info[start1:start1+length].strip()
            ret_translations.add(contact_adjective)

        # Find noun version
        start1, start2, length = SequenceMatcher(None, I_want_contact, there_was_contact).find_longest_match(0, len(I_want_contact), 0, len(there_was_contact))
        if length > 0:
            contact_noun = I_want_contact[start1:start1+length].strip()
            ret_translations.add(contact_noun)

    return ret_translations

# Tries to return a lat/lon coordinate given a url, likely languages for the page, and
# likely country of origin
# Looks for a physical address first on suspected "contact" pages ("contact us", etc)
# and then on the home page itself
def extract_location_from_site(url, languages, country_guesses):
    location = None

    # Set up browser
    user_agent = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)'
    request = Request(url)
    request.add_header('User-Agent', user_agent)
    try:
        response = urlopen(request)
    except:
        return None
    html = response.read()
    response.close()

    # Scrape the page
    soup = BeautifulSoup(html, 'html.parser')
    page_text = soup.get_text()

    # Split the url into its pieces to get the root
    split_url = url_pattern.search(url).groups()
    url_root = split_url[0] + split_url[1]

    # Translations of the word "contact" in likely page languages
    contact_translations = generate_contact_translations(languages)

    # Try to find a "contact" page
    for link in soup.find_all('a'):
        name = extractName(str(link)) # Get displayed name from tag
        if name and any([x in name.lower() for x in contact_translations]):
            contact_url = urllib.parse.urljoin(url_root, link['href'])

            # Access and scrape contact page
            contact_request = Request(contact_url)
            contact_request.add_header('User-Agent', user_agent)
            try:
                contact_response = urlopen(contact_request)
            except:
                continue
            contact_html = contact_response.read()
            contact_response.close()

            contact_soup = BeautifulSoup(contact_html, 'html.parser')
            contact_page_text = contact_soup.get_text()

            # Try to find a coordinate given the text of the "contact" page
            location = find_location_from_page(contact_page_text, country_guesses)
            if location:
                return location

    # Try to find a coordinate given the text of the page itself
    location = find_location_from_page(page_text, country_guesses)
    return location

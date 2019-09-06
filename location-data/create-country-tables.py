import csv

iso2_to_name = {}
iso3_to_name = {}
name_to_isos = {}
iso2_to_postal = {}

with open('country-info.txt', mode='r') as countries_info:
    reader = csv.reader(countries_info, delimiter='\t')
    next(reader)  # Skip headers on first line

    for row in reader:
        iso2 = row[0]
        iso3 = row[1]
        country_name = row[4]
        tld = row[9]
        # print(iso2)
        postal_code_format = row[13]
        postal_code_regex = row[14]
        languages = row[15]
        geoname_id = row[16]

        iso2_to_name[iso2] = country_name
        iso3_to_name[iso3] = country_name
        name_to_isos[country_name] = {'iso2': iso2, 'iso3': iso3}
        iso2_to_postal[iso2] = {'format': postal_code_format, 'regex': postal_code_regex}


    for k in iso2_to_postal.keys():
        # print(k, iso2_to_postal[k])

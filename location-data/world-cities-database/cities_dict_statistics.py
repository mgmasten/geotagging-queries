# This program constructs a dictionary (hash table) of the Kaggle dataset found
# at https://www.kaggle.com/max-mind/world-cities-database. See attribution in
# LICENSE.txt

# This version of the file is meant for extracting and displaying statistics
# about the datasets--mainly counting duplicate entries and city names

import csv

lat_lon_tolerance = 10

def same_coordinates(coords1, coords2):
    return (abs(coords1[0] - coords2[0]) < lat_lon_tolerance) and (abs(coords1[1] - coords2[1]) < lat_lon_tolerance)

def coordinates_exist(old_entries, new_coords):
    for entry in old_entries:
        if same_coordinates(entry, new_coords):
            return True
    return False

cities_dict = {}

duplicate_entries = 0
intracountry_same_name = 0
intercountry_same_name = 0
distinct_cities = 0
distinct_city_names = 0
max_intercountry = 0
max_intracountry = 0

two_word_cities = 0
three_word_cities = 0
more_word_cities = 0
max_city_words = 1

with open('worldcitiespop.csv', mode='r', newline='') as locations_file:
    reader = csv.reader(locations_file, delimiter=',')
    next(reader) # Skip headers on first line
    for row in reader:
        country = row[0]
        if country == 'zr':  # Zaire was renamed to Democratic Republic of the Congo
            country = 'cd'   # This dataset has entries for both names
        city = row[1]
        lat = float(row[5])
        lon = float(row[6])
        previous_entries = cities_dict.get(city)
        if previous_entries:
            matching_country_entries = previous_entries.get(country)
            if matching_country_entries:
                if coordinates_exist(matching_country_entries, (lat, lon)):
                    # print('Duplicate entry for ' + city + ' in ' + country)
                    duplicate_entries += 1
                else:
                    # print(country + ' has 2 cities called ' + city)
                    old_count = len(matching_country_entries)
                    if old_count == 1:  # This is the first new city within this country
                        intracountry_same_name += 1
                    cities_dict[city][country].append((lat, lon))
                    new_count = old_count + 1
                    if new_count > max_intracountry:
                        max_intracountry = new_count
                    distinct_cities += 1
            else:
                # print('Both ' + country + ' and ' + str([entry[0] for entry in previous_entries]) + ' have a ' + city)
                old_count = len(previous_entries)
                if old_count == 1:  # This is the first entry for another country
                    intercountry_same_name += 1
                cities_dict[city][country] = [(lat, lon)]
                new_count = old_count + 1
                if new_count > max_intercountry:
                    max_intercountry = new_count
                distinct_cities += 1
        else:
            city_words = len(city.split())
            if city_words > max_city_words:
                max_city_words = city_words
                print(city)
            if city_words == 2:
                two_word_cities += 1
            elif city_words == 3:
                three_word_cities += 1
            elif city_words > 3:
                more_word_cities += 1
            cities_dict[city] = {country: [(lat, lon)]}  # Country, lat, lon
            distinct_cities += 1
            distinct_city_names += 1

print('True duplicates:', duplicate_entries)
print('Intracountry same name:', intracountry_same_name)
print('Intercountry same name:', intercountry_same_name)
print('Total distinct cities:', distinct_cities)
print('Total distinct city names:', distinct_city_names)
print('Max intercountry:', max_intercountry)
print('Max intracountry:', max_intracountry)

print('Two word cities:', two_word_cities)
print('Three word cities:', three_word_cities)
print('More word cities:', more_word_cities)
print('Max city words:', max_city_words)

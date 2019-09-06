import csv

insert_count = 0
filename = './geonames/allCountries.txt'
city_index = 2
country_index = 8
alternate_names_index = 3
delimiter = '\t'
lat_index = 4
lon_index = 5
lat_lon_tolerance = 10
pop_limit = 100000
cities_dict = {}

def same_coordinates(coords1, coords2):
    return (abs(coords1[0] - coords2[0]) < lat_lon_tolerance) and (abs(coords1[1] - coords2[1]) < lat_lon_tolerance)

def coordinates_exist(old_entries, new_coords):
    for entry in old_entries:
        if same_coordinates(entry, new_coords):
            return True
    return False

def increment():
    global insert_count
    insert_count += 1
    if insert_count % 1000 == 0:
        print(insert_count)

def rewrite_cities_file():

    with open(filename, mode='r', newline='') as locations_file:
        reader = csv.reader(locations_file, delimiter=delimiter)
        new_file = open('./all_countries_clean_pop_lim.csv', mode='w+')
        new_file.write('id,city_name,country_iso,lat,lon\n')
        for row in reader:
            country = row[country_index]
            pop = float(row[14])
            try:
                lat = float(row[alternate_names_index]) # Works when there are no alternate names
                lon = float(row[alternate_names_index + 1])
                city_names = [row[city_index]]
            except:
                # Main name is always included in the alternate names list
                city_names = row[alternate_names_index].split(',')

                # Correct for missing tabs in allCountries.txt, which sometimes
                # lumps latitude in with alternate names
                try:
                    # Float conversion fails if this is not the latitude number but instead a name
                    lat = float(city_names[len(city_names) - 1])
                    lon = float(row[city_names_index + 1])
                    del city_names[len(city_names) - 1]
                except:
                    # There was no tab error
                    lat = float(row[lat_index])
                    lon = float(row[lon_index])

            if pop > pop_limit:
                for city_name in city_names:
                    new_line = str(insert_count + 1) + ',' + city_name + ',' + country + ',' + str(lat) + ',' + str(lon) + '\n'
                    previous_entries = cities_dict.get(city_name)
                    if previous_entries:
                        matching_country_entries = previous_entries.get(country)
                        if matching_country_entries:
                            if coordinates_exist(matching_country_entries, (lat, lon)):
                                continue
                            else:
                                cities_dict[city_name][country].append((lat, lon))
                                new_file.write(new_line)
                                increment()
                        else:
                            cities_dict[city_name][country] = [(lat, lon)]
                            new_file.write(new_line)
                            increment()
                    else:
                        cities_dict[city_name] = {country: [(lat, lon)]}  # Country, lat, lon
                        new_file.write(new_line)
                        increment()

            # for city_name in city_names:
            #     previous_entries = find_city(conn, city_name)
            #     matching_entry = False
            #     if previous_entries:
            #         for entry in previous_entries:
            #             if entry[1] == country and coordinates_exist(entry, (lat, lon)): # There's a matching entry country
            #                 matching_country = True
            #                 break

        new_file.close()

rewrite_cities_file()

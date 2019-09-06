A readme just for this version of things:

The newest version of the project does not use these big datasets, but I want a
record of them. They're too big to push to Github.

So I am keeping a folder called "BigDatasets" on my machine.

allCountries.txt goes in location-data/geonames
all_countries_clean.csv goes in location-data
worldcitiespop.csv goes in world-cities-database
pythonsqlite.db goes in the main directory (geotagging-queries)


The datasets:

- geonames was the most useful (http://download.geonames.org/export/dump/)
    - Has everything separated out into 253 countries, as well as all together
    - Has city names, countries, alternate names (including transliterations), lat/lon, postal codes, etc
    - Is also the source for the postalcode data that is still being used, as well as the language data
    - About 12 million distinct city names
    - this was the dataset I used when actually trying the city name idea, and the sqlite databases

- Kaggle was the original dataset (world-cities-database) (https://www.kaggle.com/max-mind/world-cities-database)
    - has about 2.7 million cities. Gives country, city, lat/lon, and population.
    - was just missing too many cities
    - this is the database I used in cities_dict_statistics.py

- MaxMind/Geolite (https://dev.maxmind.com/geoip/geoip2/geolite2/)
  - country and city data. 8 langs for country names
  - for cities, get lat/lon, postal code, country

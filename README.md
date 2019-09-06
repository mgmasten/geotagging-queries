# Geotagging Search Queries

This is a web application that geolocates Google search results (via IP address and/or website scraping) and plots those results on a map.

## Installation

This project requires Python3, [Flask](https://flask.palletsprojects.com/en/1.1.x/), [googletrans](https://py-googletrans.readthedocs.io/en/latest/#),
and [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

To install the necessary dependencies, run
`pip install -r requirements.txt`
to do them all at once, or install them separately.

To run the application, navigate to the home directory and run from the command line. You need to set the environment variable FLASK_APP to app.py,
and should set FLASK_ENV to development.

```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## Usage

This application was originally developed as a digital humanities research tool, but is far more general. It might be interesting as a
tool to look at how Google search operates, or at networking.

The second geolocation method--scraping pages to look for a physical address--is far less reliable than the IP geolocation and could use much
improvement. Of course, it can only ever work for sites that provide a physical address for an organization. Currently postalcodes in the US,
Canada, and Australia are well-supported, and postalcodes in Malaysia are somewhat supported.

See future-improvements.md for some of my ideas for carrying this research project further.

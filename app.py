from flask import Flask, render_template, request, jsonify
import backend
import os
import time

class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                # print('Beginning dictionary creation')
                # start = time.time()
                # backend.create_cities_dictionary(filename='./location-data/geonames/allCountries.txt',
                #                          delimiter='\t',
                #                          country_index=8,
                #                          city_index=None,
                #                          alternate_names_index=3,
                #                          isISO=True,
                #                          lat_index=4,
                #                          lon_index=5,
                #                          lat_lon_tolerance=10)
                # end = time.time()
                # print('Cities dictionary created')
                # print('It took:', end - start)

                backend.create_languages_and_tlds_dict()
                backend.create_country_dicts()
                backend.create_postalcode_dict()
                # backend.create_regex_dict()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__)
app.run()

@app.route('/')
def search():
    return render_template('main-page.html')


@app.route('/map', methods=['POST'])
def map():
    data = request.get_json()
    results = backend.get_locations(data['query'], int(data['numResults']), data['ipAddress'], data['scraping'], data['searchOptions'])
    # return jsonify(locations=results[0], frequencies=results[1], urls=results[2])
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)

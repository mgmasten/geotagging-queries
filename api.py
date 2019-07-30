from flask import Flask, render_template, request, jsonify
import backend

app = Flask(__name__)


@app.route('/')
def search():
    return render_template('main-page.html')


@app.route('/map', methods=['POST'])
def map():
    #query = request.args.get('query')
    #numResults = int(request.args.get('numResults'))
    #searchOptions = request.args.get('resultLanguage')
    data = request.get_json()
    print("Data:", data)
    #print("Search options:", searchOptions)
    #results = backend.get_locations(query, numResults, searchOptions)
    #return jsonify(locations=results[0], frequencies=results[1])


if __name__ == '__main__':
    app.run(debug=True)

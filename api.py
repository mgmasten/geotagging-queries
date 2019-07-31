from flask import Flask, render_template, request, jsonify
import backend

app = Flask(__name__)


@app.route('/')
def search():
    return render_template('main-page.html')


@app.route('/map', methods=['POST'])
def map():
    data = request.get_json()
    results = backend.get_locations(data['query'], int(data['numResults']), data['searchOptions'])
    return jsonify(locations=results[0], frequencies=results[1])


if __name__ == '__main__':
    app.run(debug=True)

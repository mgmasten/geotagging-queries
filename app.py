from flask import Flask, render_template, request, jsonify
import backend
import os
import time

app = Flask(__name__)

@app.route('/')
def search():
    return render_template('main-page.html')


@app.route('/map', methods=['POST'])
def map():
    data = request.get_json()
    results = backend.get_locations(data['query'], int(data['numResults']), data['ipAddress'], data['scraping'], data['searchOptions'])
    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

from flask import Flask, render_template, request, jsonify
import backend

app = Flask(__name__)

@app.route('/')
def search():
    return render_template('search-form.html')

@app.route('/map')
def map():
    query = request.args.get('query')
    return jsonify(locations=backend.get_locations(query))

if __name__ == '__main__':
   app.run(debug = True)

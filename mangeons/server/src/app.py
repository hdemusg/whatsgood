from re import split
from flask import Flask, request, render_template, make_response, send_from_directory
import os
import time
import requests
import json
from bs4 import BeautifulSoup
from werkzeug.utils import redirect

import yelp

app = Flask(__name__, static_url_path='')

def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)

@app.route('/search', methods=['GET'])
def index_post():
    keywords = request.args.get('searchterm')
    lat = float(request.args.get('lat'))
    long = float(request.args.get('long'))

    search_results = yelp.search_businesses(keywords, (lat, long))
    businesses = search_results['businesses']

    page = render_template('results.html', context=search_results)
    response = make_response(page)
    return response

@app.get('/')
def index():
    context = {'server_time': format_server_time()}
    template = render_template('index.html', context=context)
    response = make_response(template)
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    return response

@app.get('/biz/<id>')
def getReviews(id):
    details = yelp.getBizDetailsAndReviews(id)
    template = render_template('restaurant.html', context=details)
    ret = make_response(template)
    ret.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    return ret

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
    # app.run(debug=True)


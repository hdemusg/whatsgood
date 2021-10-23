from flask import Flask, request, render_template, make_response
import os
import time
import requests
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

token = "gWjr-4eZ8Edx6-nhNLg4OORGUy9JeqHQH5h0sJ78NzLiMxljSN_kqphbhfwzTpc8ghEjRCfp0pWRGiCC38msbeZkpqbtOJfVbEQER6rpHDZLcEeLP4aDb5_-ZzN0YXYx"
auth = {'Authorization': 'Bearer ' + token}

def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        d = request.form.to_dict()
        keywords = d['keyword']
        lat = float(d['lat'])
        lon = float(d['lon'])
        params = {"term": keywords, "latitude": lat, "longitude": lon}
        response = requests.get('https://api.yelp.com/v3/businesses/search', params=params, headers=auth)
        j = response.json()
        if len(j["businesses"]) > 0:
            b = j["businesses"][0]["id"]
            business = j["businesses"][0]
            #print(business)
            review_url = f'https://api.yelp.com/v3/businesses/{b}/reviews'
            resp_rev = requests.get(review_url, headers=auth)
            r = resp_rev.json()
            reviews = dict()
            for r in r["reviews"]:
                reviews[r["text"]] = r["rating"]
            #print(reviews)
            a = j["businesses"][0]["alias"]
            scrape_url = f"https://yelp.com/biz/{a}"
            scrape = requests.get(scrape_url)
            #print(scrape.text)
            soup = BeautifulSoup(scrape.text, 'html.parser')

            ul = soup.find_all(class_=" review__373c0__3MsBX border-color--default__373c0__1WKlL")
            print(ul)
            #names = j["businesses"]
            #print(scrape_url)
            #ret = keywords + str(lat) + str(lon)
            add = business['location']["display_address"]
            address = ""
            for a in add[:-1]:
                #print(a)
                address += a + " "
            address = address[:-1]
            address += ', ' + add[-1]
            context = {'name': business["name"], 'address': address, 'reviews': reviews.keys()}
            template = render_template('results.html', context=context)
            ret = make_response(template)
            ret.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
            return ret
        else:
            return "No results found."
        
    else:
        context = {'server_time': format_server_time()}
        template = render_template('index.html', context=context)
        response = make_response(template)
        response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
        return response

@app.route('/get-name/<id>',methods=['GET'])
def getName(id):
    url = f"https://api.yelp.com/v3/businesses/{id}"
    response = requests.get(url, headers=auth)
    j = response.json()
    b = j["name"]
    a = j["alias"]
    print(a)
    return b

    #SsO1q915qPriqziI90ZmOA

'''
@app.route('/results',methods=['POST'])
def res():
''' 

if __name__ == "__main__":
    #app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
    app.run(debug=True)


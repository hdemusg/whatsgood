import asyncio
import bs4
from concurrent.futures import ProcessPoolExecutor
from requests import Session
from requests_futures.sessions import FuturesSession

session = FuturesSession(executor=ProcessPoolExecutor(max_workers=10),
                         session=Session())

token = "gWjr-4eZ8Edx6-nhNLg4OORGUy9JeqHQH5h0sJ78NzLiMxljSN_kqphbhfwzTpc8ghEjRCfp0pWRGiCC38msbeZkpqbtOJfVbEQER6rpHDZLcEeLP4aDb5_-ZzN0YXYx"
auth = {'Authorization': f'Bearer {token}'}

headers = {}
headers.update(auth)

cache = {}
def cachefunc(func):
    def cachedfunc(*args):
        key = tuple(args)
        if key in cache:
            return cache[key]
        else:
            cache[key] = func(*args)
            return cache[key]
    return cachedfunc

async def getAllPages(alias):
    REVIEWS_PER_PAGE = 10
    NUM_REVIEWS = 100
    url = f'https://www.yelp.com/biz/{alias}'
    requests = [session.get(url, params={"start": start}) for start in range(0, NUM_REVIEWS + 1, REVIEWS_PER_PAGE)]
    pages = [req.result().text for req in requests]
    return pages

def parseStarLabel(star_elem):
    return float(star_elem['aria-label'].split()[0])

def getBizReviews(soups):
    reviews = []
    for soup in soups:
        reviews_elems = soup.select('div.review__373c0__3MsBX p.comment__373c0__Nsutg span')
        stars_elems = soup.select('div.review__373c0__3MsBX div.i-stars__373c0___sZu0')
        for review_elem, star_elem in zip(reviews_elems, stars_elems):
            review = review_elem.text
            stars = parseStarLabel(star_elem)
            reviews.append({"review": review, "stars": stars})
    return reviews

def getBizStars(soup):
    star_elem = soup.select('div.photo-header-content__373c0__2P1Jy div.i-stars__373c0___sZu0')
    return parseStarLabel(star_elem[0])

@cachefunc
async def getBizInfo(id):
    URL = f'https://api.yelp.com/v3/businesses/{id}'
    details = session.get(URL, headers=headers).result().json()
    return details

async def getBizReviewsAsync(alias):
    pages = await getAllPages(alias)
    soups = [bs4.BeautifulSoup(page, 'html.parser') for page in pages]
    reviews = getBizReviews(soups)
    return {"reviews": reviews}

def search_businesses(search_term, location):
    URL = 'https://api.yelp.com/v3/businesses/search'
    lat, long = location
    params = {"term": search_term, "latitude": lat, "longitude": long}
    return session.get(URL, params=params, headers=headers).result().json()

# @cachefunc
def getBizDetails(id):
    details = asyncio.run(getBizInfo(id))
    return {
        "name": details['name'],
        "address": " ".join(details['location']['display_address']),
        "image_url": details['image_url'],
        "url": details['url'],
        "phone": details['display_phone'],
        "alias": details['alias'],
        "stars": details['rating']
    }

@cachefunc
def search_businesses(search_term, location):
    URL = 'https://api.yelp.com/v3/businesses/search'
    lat, long = location
    params = {"term": search_term, "latitude": lat, "longitude": long}
    return session.get(URL, params=params, headers=headers).result().json()

@cachefunc
def getBizDetailsAndReviews(id):
    details = getBizDetails(id)
    alias = details['alias']
    reviews = asyncio.run(getBizReviewsAsync(alias))
    details.update(reviews)
    return details


# soup.select('h1')[0].contents
# reviews = soup.select('p.comment__373c0__Nsutg span')
# # for review in reviews:
# #     print(review.text)
# print(len(reviews))
if __name__ == '__main__':
    getBizDetails('chipotle-mexican-grill-atlanta-11')




from flask import Flask, render_template, request, url_for
import requests
from bs4 import BeautifulSoup
from time import sleep
import aiohttp
import asyncio



app = Flask(__name__)
BASE_URL = "https://www.flipkart.com"
HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',  
           'Accept-Language' : 'en-US,en;q=0.5',
           'ngrok-skip-browser-warning' : 'true'}


@app.route("/")
def home():
    return render_template("home.html")
    


@app.route("/index")
def index():
    query_param = request.args['product']
    urls = create_urls(query_param)
    results = asyncio.run(get_product_html(urls))
    result = parse(results)                              
    return render_template('content.html', data = result, length = len(result), links = urls)
    #return result

def create_urls(param):
    links = ['proxy']
    CLASS_LIST = ['s1Q9rs', '_2UzuFa', '_1fQZEK']
    for page in range(1,3):
        url = f'https://www.flipkart.com/search?q={param}&page={page}'
        # webpage = requests.get(url, headers = HEADERS)
        webpage = ''
        while webpage == '':
            try:
                webpage = requests.get(url, headers = HEADERS)
                break
            except requests.exceptions.ConnectionError:
                print('sleep')
                sleep(5)
                continue 

        if webpage.status_code == 200 :
            soup = BeautifulSoup(webpage.content, 'html.parser')
            tags = soup.findAll('a', class_ = CLASS_LIST)
            for i in range(len(tags)):
                link = BASE_URL + tags[i].get('href')
                links.append(link)


    return links[1:]

def get_title(soup):
    try:
        title_tag = soup.find("span", {"class" : "B_NuCI"})
        title = title_tag.text
    except AttributeError:
        title = ""

    return title

def get_reviews(soup):
    try:
        review_tag = soup.find("div", {"class" : "_3LWZlK"})
        review = review_tag.text

    except AttributeError:
        review = ""
    
    return review

def get_price(soup):
    try:
        price_tag = soup.find("div", {"class": "_30jeq3 _16Jk6d"})
        price =  price_tag.text.strip()[1:]

    except AttributeError:
        price = ""
    
    return price

def get_discount(soup):
    try:
        discount_tag = soup.find("div",{"class" : "_3Ay6Sb _31Dcoz"}).span
        discount = discount_tag.text

    except AttributeError:
        discount = "No Discount"

    return discount

def parse(results):
    result_list = []
    for html in results:
        product_json = {}
        soup = BeautifulSoup(html, 'html.parser') 
        product_json['title'] = get_title(soup)
        product_json['rating'] = get_reviews(soup)
        product_json['price'] = get_price(soup)
        product_json['discount'] = get_discount(soup)

        result_list.append(product_json)

    return result_list

async def get_page(session, url):
    async with session.get(url, ssl=False) as r:
        return await r.text()
    

async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def get_product_html(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        return data


if __name__ == '__main__':
    app.run(port=8000,debug=True)
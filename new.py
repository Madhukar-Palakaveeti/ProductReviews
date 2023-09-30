import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio



BASE_URL = "https://www.flipkart.com"
search_term = input("Enter a search term: ")
RESULT_LIST = []
HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',  'Accept-Language' : 'en-US,en;q=0.5'}
def create_links(search_term):
    links = []
    for page in range(1,6):
        url = f'https://www.flipkart.com/search?q={search_term}&page={page}'
        webpage = requests.get(url, headers = HEADERS)
        soup = BeautifulSoup(webpage.content, 'html.parser') 
        class_list = ['s1Q9rs', '_2UzuFa', '_1fQZEK']
        links_tag = soup.findAll("a", class_ = class_list)
        for i in range(len(links_tag)):
            new_link = BASE_URL + links_tag[i].get('href')
            links.append(new_link)
    return links

async def get_page(session, url):
    async with session.get(url) as r:
        return await r.text()
    

async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def main(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        return data


def get_content(results):
    for html in results:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find("span", {"class" : "B_NuCI"})
        title = title_tag.text
        print(title)
    return
     


if __name__ == '__main__':
    urls = create_links(search_term)
    results = asyncio.run(main(urls))
    get_content(results)


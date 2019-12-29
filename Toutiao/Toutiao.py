import json
from hashlib import md5
import os
import requests
from bs4 import BeautifulSoup
import re
import codecs
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def get_page_index(offset, keyword):
    """
    :param offset: 翻页
    :param keyword: 搜索关键字
    :return: 本页内容
    """
    params = {
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis',
    }
    headers = {
        'cookie': 'tt_webid=6726420735470077454; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6726420735470077454; csrftoken=e826e0c3c32a74555da7ec10112dc449; UM_distinctid=16ca3d7c13388-08bc3bd0b608e-c343162-144000-16ca3d7c1353a0; CNZZDATA1259612802=568057237-1566113713-https%253A%252F%252Fwww.toutiao.com%252F%7C1566113713; _ga=GA1.2.343540482.1566116922; __tasessionId=tiuwzvodh1566809947037; s_v_web_id=3c58c92ef3181a0e355d8348267b5efa',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    }
    base_url = "https://www.toutiao.com/api/search/content/?"
    html = requests.get(url=base_url, params=params, headers=headers)
    return html

def get_aiticle_url(html):
    """
    :param html: 主页链接
    :return: 本页文章链接
    """
    data = html.json()
    if data and "data" in data.keys():
        for item in data.get("data"):
            if item.get("article_url") != None:
                yield item.get("article_url")

def get_page_detail(url):
    """
    :param url: Article link
    :return: Article content
    """
    headers = {
        'cookie': 'tt_webid=6726420735470077454; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6726420735470077454; csrftoken=e826e0c3c32a74555da7ec10112dc449; UM_distinctid=16ca3d7c13388-08bc3bd0b608e-c343162-144000-16ca3d7c1353a0; CNZZDATA1259612802=568057237-1566113713-https%253A%252F%252Fwww.toutiao.com%252F%7C1566113713; _ga=GA1.2.343540482.1566116922; __tasessionId=tiuwzvodh1566809947037; s_v_web_id=3c58c92ef3181a0e355d8348267b5efa',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    }
    html = requests.get(url=url, headers=headers)
    return html

def parse_page_detail(html):
    """
    :param html: Article content
    :return: Article image links
    """
    soup = BeautifulSoup(html.text, "lxml")
    title = soup.select("title")[0].get_text()
    print(title)
    image_pattern = re.compile('JSON.parse\(\\\"(.*?)\\\"\),', re.S)
    result = re.search(image_pattern, html.text)
    data = result.group(1).replace('\\\\', '\\')
    data = data.replace('\\\"', '\"')
    data = json.loads(data)
    sub_images = data.get("sub_images")
    for item in sub_images:
        url = item.get("url")
        url = codecs.decode(url, 'unicode-escape') # image url
        save_to_db(url)
        # save to local
        content = download(url)
        save_images(content)

def save_to_db(url):
    if db[MONGO_TABLE].insert(url):
        print("save success." + url)
    else:
        print("save error!")

def download(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except:
        print("Ask error, " + url)
        return None

def save_images(content):
    file_path = "{0}{1}.{2}".format(os.getcwd(), md5(content), "jpg") # current file
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(content)
            f.close()

def main(pages, keyword):
    for i in range(0, pages+1):
        # 0 20 40
        page = i * 20
        html = get_page_index(page, keyword)
        print("--第", i+1, "页--")
        article_url_list = get_aiticle_url(html)
        for item in article_url_list:
            if (item != None):
                print(item)
                data = get_page_detail(item)
                if data:
                    try:
                        parse_page_detail(data)
                    except:
                        pass




if __name__ == '__main__':
    main(2, "街拍")


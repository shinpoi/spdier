# -*- coding: utf-8 -*-
# python 3.5
# first spider


import urllib3
import json
from bs4 import BeautifulSoup


url_id = {'homeraji':'home'}
url_json = 'http://www.onsen.ag/data/api/getMovieInfo/'
url_homepage = 'http://www.onsen.ag/index.html?pid=home'
save_path = '-------'
file_name = '-------'
info_file_name = 'info.txt'


def get_json(url):
    page_bytes = urllib3.PoolManager().request('GET', url)
    page_json = json.loads(page_bytes.data[9:-3].decode('utf-8'))
    return page_json


def get_info(page_json):
    info = {}
    info['date'] = page_json['update']
    info['count'] = page_json['count']
    info['title'] = page_json['title']
    return info


def get_guest(homepage):
    html = urllib3.PoolManager().request('GET', homepage)
    soup = BeautifulSoup(html.data, 'lxml')
    info = soup.find(id='home')
    guest = info['data-guest']
    return guest


def get_mp3(page_json):
    mp3_url = page_json['moviePath']['pc']
    mp3_file = urllib3.PoolManager().request('GET', mp3_url)
    return mp3_file.data


def save_files(file, path):
    with open(path, 'wb') as f:
        f.write(file)
    return 1


def add_info(info, info_path):
    message = "%s 第%s回 Guest:%s Date:%s \n" % (info['title'], info['count'], info['guest'], info['date'])
    with open(info_path, 'a') as f:
        f.write(message)


# run
uj = url_json + url_id['homeraji']
page_json = get_json(uj)
info = get_info(page_json)
info['guest'] = get_guest(url_homepage)
mp3 = get_mp3(page_json)
save_files(mp3, save_path + file_name)
add_info(info, save_path + info_file_name)

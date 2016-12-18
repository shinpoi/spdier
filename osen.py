# -*- coding: utf-8 -*-
# python 3.5
# first spider

import os
import time
import urllib3
import json
from bs4 import BeautifulSoup

url_json = 'http://www.onsen.ag/data/api/getMovieInfo/'
url_homepage = 'http://www.onsen.ag/index.html?pid=home'

###################################
# parameter
url_id = {'homeraji':'home'}
save_path = '/home/aoi-lucario/tools/'
info_file_name = 'info.txt'

###################################
# init
time_ = time.strftime("%Y/%m/%d (%A) - %H:%M:%S")

# local: 'log.txt', 'flag.json'; path: 'info.txt', 'xxx.mp3'

# log (if not, build one)
if not os.path.exists('./log.txt'):
    with open('log.txt', 'w') as f:
        f.write('#### log of onsen spider ####\nbuild in %s \n\n' % time_)
else:
    with open('log.txt', 'a') as f:
        f.write('\n#### restart at %s\n\n' % time_)

# info (if not, build one)
if not os.path.exists(save_path + info_file_name):
    with open(save_path + info_file_name, 'w') as f:
        f.write('#### onsen info ####\nbuild in %s \n\n' % time_)

# flag (read flag.json, if not, flag -> None)
if os.path.exists('./flag.json'):
    with open('flag.json', 'r') as f:
        flag = json.loads(f.read())
else:
    flag = {'homeraji': {'count': None}}


###################################
# spider function
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
    soup = BeautifulSoup(html.data, 'html5lib')
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
    with open('log.txt', 'a') as f:
        f.write('[write]!!!!! write file \'%s\'  at %s \n' % (path, time.strftime("%Y/%m/%d (%A) - %H:%M:%S")))


def add_info(info, info_path):
    message = "%s 第%s回 -- ゲスト:%s アップデート:%s \n" % (info['title'], info['count'], info['guest'], info['date'])
    with open(info_path, 'a') as f:
        f.write(message)

    with open('log.txt', 'a') as f:
        f.write('[info]!!! write info \'%s\'  at %s \n\n' % (info_path, time.strftime("%Y/%m/%d (%A) - %H:%M:%S")))

    # update flag.json
    w = {'homeraji': {'count': info['count']}}
    jw = json.dumps(w)
    with open('flag.json', 'w') as f:
        f.write(jw)

while True:
    # print("add log at %s" % time_)
    with open('log.txt', 'a') as f:
        f.write('[awake] awake at %s \n' % time.strftime("%Y/%m/%d (%A) - %H:%M:%S"))

    if time.strftime("%H") == '23':
        # print("add info at %s" % time_)
        with open('log.txt', 'a') as f:
            f.write('[scan] scan at %s \n' % time.strftime("%Y/%m/%d (%A) - %H:%M:%S"))

        # spider for homeraji
        uj = url_json + url_id['homeraji']
        page_json = get_json(uj)
        info = get_info(page_json)
        if flag['homeraji']['count'] != info['count']:
            info['guest'] = get_guest(url_homepage)
            file_name = 'ほめらじ-' + info['count'] + '.mp3'
            mp3 = get_mp3(page_json)
            save_files(mp3, save_path + file_name)
            add_info(info, save_path + info_file_name)
            flag = {'homeraji': {'count': info['count']}}
            print("add new file: %s at %s" % (file_name, time.strftime("%Y/%m/%d (%A) - %H:%M:%S")))
    time.sleep(60*60)

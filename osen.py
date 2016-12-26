# -*- coding: utf-8 -*-
# python 3.5
# first spider

import os
import time
import urllib3
import json
from bs4 import BeautifulSoup
import logging
import re

###################################
# parameter
url_id = {'homeraji':'home'}
save_path = '/home/aoi-lucario/osen/'
info_file_name = 'info.md'
log_file_name = 'osen_spider.log'

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename=log_file_name,
                    filemode='a')

url_json = 'http://www.onsen.ag/data/api/getMovieInfo/'
url_homepage = 'http://www.onsen.ag/index.html?pid=home'

###################################
# init
time_ = time.strftime("%Y/%m/%d (%A) - %H:%M:%S")

# local: log_file_name, 'flag.json'; path: 'info.txt', 'xxx.mp3'

# log (if not, build one)
if not os.path.exists('./'+log_file_name):
    with open(log_file_name, 'w') as f:
        f.write('#### log of onsen spider ####\nbuild in %s \n\n' % time_)
else:
    with open(log_file_name, 'a') as f:
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
    pattern = re.compile(r'{.*}')
    re1 = re.search(pattern, page_bytes.data.decode('utf-8'))
    page_json = json.loads(re1.group())
    return page_json


def get_info(page_json):
    info = {}
    info['date'] = page_json['update']
    info['count'] = page_json['count']
    info['title'] = page_json['title']
    return info


def get_guest(homepage, bangumi_id='home'):
    html = urllib3.PoolManager().request('GET', homepage)
    soup = BeautifulSoup(html.data, 'html5lib')
    info = soup.find(id=bangumi_id)
    guest = info['data-guest']
    return guest


def get_mp3(page_json):
    mp3_url = page_json['moviePath']['pc']
    mp3_file = urllib3.PoolManager().request('GET', mp3_url)
    return mp3_file.data


def save_files(file, file_name, path=save_path):
    with open(path+file_name, 'wb') as f:
        f.write(file)
    logging.warning('!!!Write files (%s)' % file_name)


def add_info(info, path=save_path, file_name=info_file_name):
    message = "%s 第%s回 -- ゲスト:%s アップデート:%s \n" % (info['title'], info['count'], info['guest'], info['date'])
    with open(path+file_name, 'a') as f:
        f.write(message)

    logging.warning('!!Write info')

    # update flag.json
    w = {'homeraji': {'count': info['count']}}
    jw = json.dumps(w)
    with open('flag.json', 'w') as f:
        f.write(jw)

while True:
    logging.debug('awake')

    if time.strftime("%H") == '16':
        logging.info('scan')

        # spider for homeraji
        uj = url_json + url_id['homeraji']
        page_json = get_json(uj)
        info = get_info(page_json)
        if flag['homeraji']['count'] != info['count']:

            mp3 = get_mp3(page_json)
            file_name = 'Home-' + info['count'] + '.mp3'
            save_files(mp3, file_name=file_name)

            try:
                info['guest'] = get_guest(url_homepage)
            except KeyError as e:
                info['guest'] = 'No Data'
                logging.warning('No guest data in %s' % file_name)
            add_info(info)

            flag = {'homeraji': {'count': info['count']}}
            print("add new file: %s at %s" % (file_name, time.strftime("%Y/%m/%d (%A) - %H:%M:%S")))
    time.sleep(60*60)

# - coding: utf-8 -*-
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
pwd = os.path.dirname(__file__) + '/'

id_list = {'home':{'info_file_name':'info_home.txt', 'save_name':'Home-', 'subpath':'homeraji/'},
        'otomain':{'info_file_name':'info_otomain.txt', 'save_name':'Otomain-', 'subpath':'otomain/'},
		'homeomake':{'info_file_name':'', 'save_name':'Homeomake-', 'subpath':'homeraji_omake/'}}

save_path = '"---------"'
log_file_name = pwd + 'osen_spider.log'

query_json = 'http://www.onsen.ag/data/api/getMovieInfo/'
url_homepage = 'http://www.onsen.ag/index.html?pid=home'

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename=log_file_name,
                    filemode='a')

###################################
# init
time_ = time.strftime("%Y/%m/%d (%A) - %H:%M:%S")

# local: 'log_file_name.log', 'flag.json'
# path: 'info.txt', 'xxx.mp3'

try:
    os.makedirs(save_path)
    logging.warning('makedir %s' % save_path)
except FileExistsError:
    pass

for i in id_list:
    try:
        os.makedirs(save_path + id_list[i]['subpath'])
        logging.warning('makedir %s' % save_path + id_list[i]['subpath'])
    except FileExistsError:
        pass

# log (if not, build one)
if not os.path.exists(log_file_name):
    with open(log_file_name, 'w') as f:
        f.write('#### log of onsen spider ####\nbuild in %s \n\n' % time_)

# info (if not, build one)
for i in id_list:
    info_file_name = id_list[i]['info_file_name']
    if not os.path.exists(save_path + info_file_name):
        with open(save_path + info_file_name, 'w') as f:
            f.write('#### onsen info ####\nbuild in %s \n\n' % time_)

# flag (read flag.json, if not, flag -> None)
if os.path.exists(pwd + 'flag.json'):
    with open(pwd + 'flag.json', 'r') as f:
        flag = json.loads(f.read())
else:
    flag = {}
    for x in id_list:
        flag[x] = {'count': None}

# check flag:
bangumi = [i for i in id_list.keys()]
for i in bangumi:
    try:
        flag[i]['count']
    except KeyError:
        flag[i]['count'] = None

###################################
# Spider


class Spider(object):
    def __init__(self, id_list, save_path, query_json, url_homepage, flag):
        self.id_list = id_list
        self.save_path = save_path
        self.query_json = query_json
        self.url_homepage = url_homepage
        self.flag = flag
        self.pwd = os.path.dirname(__file__) + '/'

    @staticmethod
    def get_json(url):
        page_bytes = urllib3.PoolManager().request('GET', url)
        pattern = re.compile(r'{.*}')
        re1 = re.search(pattern, page_bytes.data.decode('utf-8'))
        page_json = json.loads(re1.group())
        return page_json

    def get_info(self, bangumi_id):
        url = self.query_json + bangumi_id
        page_json = self.get_json(url)

        # get json_info
        info = {}
        info['date'] = page_json['update']
        info['count'] = page_json['count']
        info['title'] = page_json['title']
        info['download'] = page_json['moviePath']['pc']

        # get guest
        html = urllib3.PoolManager().request('GET', self.url_homepage)
        soup = BeautifulSoup(html.data, 'html5lib')
        try:
            info['guest'] = soup.find(id=bangumi_id)['data-guest']
        except KeyError:
            info['guest'] = 'No Data'
	except TypeError:
	    info['guest'] = 'No Data'
            #logging.warning('No guest data in %s - %s' % (bangumi_id, info['count']))
        return info

    def save_files(self, file_data, file_name):
        with open(self.save_path + file_name, 'wb') as f:
            f.write(file_data)
        logging.warning('!!!Write files (%s)' % file_name)

    def add_info(self, info, bangumi_id):
        file_name = self.id_list[bangumi_id]['info_file_name']
            if file_name:
            message = "%s 第%s回 -- ゲスト:%s アップデート:%s \n" % (info['title'], info['count'], info['guest'], info['date'])
            with open(self.save_path + file_name, 'a') as f:
                f.write(message)

        logging.warning('!!Write info %s - %s' % (bangumi_id, info['count']))

        # update flag.json
        self.flag[bangumi_id]['count'] = info['count']
        json_flag = json.dumps(flag)
        with open(self.pwd + 'flag.json', 'w') as f:
            f.write(json_flag)

    def run(self):
        logging.info('scan')
        print('scanning! ')
        for bangumi_id in self.id_list:
            info = self.get_info(bangumi_id)
            if flag[bangumi_id]['count'] != info['count']:
                logging.warning('%s has update!' % info['title'])
                audio = urllib3.PoolManager().request('GET', info['download']).data
                save_name = self.id_list[bangumi_id]['subpath'] + self.id_list[bangumi_id]['save_name'] + info['count'] + '.mp3'
                self.save_files(file_data=audio, file_name=save_name)
                self.add_info(info=info, bangumi_id=bangumi_id)
                print("add new file: %s at %s" % (save_name, time.strftime("%Y/%m/%d (%A) - %H:%M:%S")))


# Spider END
###################################

spider = Spider(id_list=id_list, save_path=save_path, query_json=query_json, url_homepage=url_homepage, flag=flag)
spider.run()

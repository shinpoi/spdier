# - coding: utf-8 -*-
# python 3.5
# first spider

import os
import time
import requests
import json
from bs4 import BeautifulSoup
import logging
import re


###################################
# parameter
pwd = os.path.dirname(__file__) + '/'
log_file_name = pwd + 'osen_spider.log'
save_path = '---------------'
# local: 'log_file_name.log'
# path: 'info.json', 'xxx.mp3'

id_list = {'home':{'info_file_name':'homeraji.json', 'save_name':'Home-', 'subpath':'homeraji/'},
        'otomain':{'info_file_name':'otomain.json', 'save_name':'Otomain-', 'subpath':'otomain/'},
		'homeomake':{'info_file_name':'homeraji_omake.json', 'save_name':'Homeomake-', 'subpath':'homeraji_omake/'}}

query_json = 'http://www.onsen.ag/data/api/getMovieInfo/'
url_homepage = 'http://www.onsen.ag/index.html'

logging.basicConfig(level=logging.WARNING,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename=log_file_name,
                    filemode='a')

###################################
# init
time_ = time.strftime("%Y/%m/%d (%A) - %H:%M:%S")

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

###################################
# Spider


class Spider(object):
    def __init__(self, id_list, save_path, query_json, url_homepage):
        self.id_list = id_list
        self.save_path = save_path
        self.query_json = query_json
        self.url_homepage = url_homepage
        self.flag = {}
        self.pwd = os.path.dirname(__file__) + '/'
        
    def local_info(self, key, info_file_dir):
        try:
            with open(info_file_dir) as f:
                li = json.loads(f.read())
                if li:
                    self.flag[key] = li[-1]['n']
                else:
                    li = []
                    self.flag[key] = 0
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            li = []
            self.flag[key] = 0
        return li

    @staticmethod
    def get_json(url):
        page_bytes = requests.get(url).content
        pattern = re.compile(r'{.*}')
        re1 = re.search(pattern, page_bytes.decode('utf-8'))
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
        html = requests.get(self.url_homepage).content
        soup = BeautifulSoup(html, 'html5lib')
        try:
            info['guest'] = soup.find(id=bangumi_id)['data-guest']
        except (KeyError, TypeError):
            info['guest'] = ''
        return info

    def save_files(self, file_data, file_name):
        with open(self.save_path + file_name, 'wb') as f:
            f.write(file_data)
        logging.warning('!!!Write files (%s)' % file_name)

    def add_info(self, info, bangumi_id, local_list):
        file_name = self.id_list[bangumi_id]['info_file_name']
        local_list.append({'n':info['count'], 'd':info['date'], 'g':info['guest']})
        with open(self.save_path + file_name, 'w') as f:
            f.write(json.dumps(local_list))
        logging.warning('!!Write info %s - %s' % (bangumi_id, info['count']))

    def run(self):
        logging.warning('scan')
        for bangumi_id in self.id_list:
            print('scanning!', bangumi_id)
            local_list = self.local_info(bangumi_id, save_path+self.id_list[bangumi_id]['info_file_name'])
            info = self.get_info(bangumi_id)
            if self.flag[bangumi_id] != info['count']:
                logging.warning('update %s ...' % info['title'])
                audio = requests.get(info['download']).content
                save_name = self.id_list[bangumi_id]['subpath'] + self.id_list[bangumi_id]['save_name'] + info['count'] + '.mp3'
                self.save_files(file_data=audio, file_name=save_name)
                self.add_info(info=info, bangumi_id=bangumi_id, local_list=local_list)
                print("add new file: %s at %s" % (save_name, time.strftime("%Y/%m/%d (%A) - %H:%M:%S")))


# Spider END
###################################

spider = Spider(id_list=id_list, save_path=save_path, query_json=query_json, url_homepage=url_homepage)
spider.run()

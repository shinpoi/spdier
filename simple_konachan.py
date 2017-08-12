# - coding: utf-8 -*-
# python 3.5
# claw pages by tags form 0 to max

import os
import time
import requests
from bs4 import BeautifulSoup
import logging
import re


#######################################
# set logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename='konachan_' + time.strftime('%Y-%m-%d_%H-%M') + '.log',
                    filemode='a'
                    )

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s]  \t%(message)s\t')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

#######################################


class Spider(object):
    def __init__(self):
        self.host = 'http://konachan.com'
        self.tags = ('rating:safe', 'touhou')
        self.header_base = self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.84 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Host': 'konachan.com',
            'Referer': 'http://konachan.com/',
        }
        self.cookies = None
        self.url_base = self.host + '/post?tags='
        self.save_path = './konachan/'
        for tag in self.tags:
            self.url_base += tag + '+'
        if self.url_base.endswith('+'):
            self.url_base = self.url_base[:-1] + '&'

        try:
            os.mkdir(self.save_path)
            logging.info('create save path')
        except OSError:
            pass

    # get cookies
    def get_cookies(self):
        hp = requests.get(self.host, headers=self.header_base)
        self.cookies = hp.cookies
        logging.info('get cookies success')

    # Update cookies. | Success:  updated cookies;
    def update_cookies(self, new_cookies):
        # cookies -> json
        origin = requests.utils.dict_from_cookiejar(self.cookies)
        neo = requests.utils.dict_from_cookiejar(new_cookies)
        # update
        for i in neo:
            origin[i] = neo[i]
        # json -> cookies
        self.cookies = requests.utils.cookiejar_from_dict(origin)
        logging.debug('update cookies')

    def get_max_page(self):
        res = requests.get(self.url_base[:-1], headers=self.header_base, cookies=self.cookies)
        soup = BeautifulSoup(res.content, 'lxml')
        max_page = int(soup.find(class_='pagination').findAll('a')[-2].text)
        self.update_cookies(res.cookies)
        logging.info('has %d pages' % max_page)
        return max_page

    # get a soup, save each image
    def parse_page(self, soup, pattern=re.compile('show/([0-9]+)/')):
        url_list = [i['href'] for i in soup.findAll(class_='thumb')]
        header = self.header_base
        for url in url_list:
            time.sleep(1)
            name = pattern.search(url).groups()[0]
            res = requests.get(self.host + url)
            soup = BeautifulSoup(res.content, 'lxml')
            src_url = soup.find(id='image')['src']
            header['Referer'] = self.host + url
            expand = src_url[-4:]
            if not expand.startswith('.'):
                expand = '.' + expand
            data = requests.get('http:' + src_url, headers=header, timeout=60)
            if data.status_code == 200:
                logging.debug("save image: %s" % name+expand)
                with open(self.save_path + name + expand, 'wb') as f:
                    f.write(data.content)
            else:
                logging.warning("get %s failed!!" % name+expand)

    def run(self):
        self.get_cookies()
        max_page = self.get_max_page()
        for i in range(1, max_page):
            logging.info('start scan page: %d' % i)
            res = requests.get(self.url_base + 'page=%d' % i, headers=self.header_base, cookies=self.cookies)
            self.update_cookies(res.cookies)
            self.parse_page(BeautifulSoup(res.content, 'lxml'))


#############################
if __name__ == "__main__":
    spider = Spider()
    spider.run()


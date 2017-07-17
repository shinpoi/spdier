# - coding: utf-8 -*-
# python 3.5
# a spider pull image from safebooru.org by tags

import os
import time
import requests
from bs4 import BeautifulSoup
import logging
import re
import numpy as np
import cv2

#######################################
# set logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename='safebooru_' + time.strftime('%Y-%m-%d_%H-%M') + '.log',
                    filemode='a'
                    )

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s]  \t%(message)s\t')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

#######################################
# set parameter

tag = ('face', 'solo', '1girl', 'close-up')
de_tag = ('comic', 'monochrome', 'bangs', 'tongue', 'ass', 'shoes')
count = 40

dir_root = './'
dir_origin = dir_root + 'origin/'
dir_filter = dir_root + 'filter/'

size = 150
page = 99999

#######################################


class Spider(object):
    def __init__(self):
        self.host = 'http://safebooru.org/'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.84 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep - alive',
            'Referer': 'about:blank',
        }
        self.dir_origin = dir_origin
        self.dir_filter = dir_filter
        for i in (self.dir_origin, self.dir_filter):
            try:
                os.mkdir(i)
            except OSError:
                pass

        self.size = size
        self.count = count
        self.de_tag = de_tag
        self.page = page
        self.pid_now = 0
        # set
        self.tags = ''
        for i in tag:
            self.tags += i + '+'
        if self.tags.endswith('+'):
            self.tags = self.tags[:-1]
        self.page_now = self.host + 'index.php?page=post&s=list&tags=' + self.tags

    # check <self.page_now> to next page, return a soup
    def get_next_page(self, pattern=re.compile('pid=([0-9]+)')):
        url = self.page_now
        self.header['Referer'] = self.page_now

        if 'pid=' not in url:
            pid = '0'
            url += '&pid=' + pid
        else:
            pid = int(pattern.search(url).groups()[0])
            url = pattern.sub('pid=%s' % str(int(pid+self.count)), url)

        res = requests.get(url, headers=self.header, timeout=15)
        logging.debug('url = %s' % url)
        self.page_now = url
        self.pid_now = int(pid)
        if res.status_code == 200:
            logging.info('get index_page(pid=%s) succeed!' % pid)
            soup = BeautifulSoup(res.text, 'lxml')
        else:
            logging.error("get index_page(pid=%s) failed! status_code=%d" % (pid, res.status_code))
            raise ValueError
        return soup

    # return a list of images's url  // check tags
    def parse_page(self, soup):
        imgs = soup.findAll(class_='thumb')
        if not imgs:
            logging.warning('not find any imags in this page!')

        src_list = []
        for img_obj in imgs:
            # check tags
            tags = img_obj.img['alt'].split(' ')
            flag = 0
            for tag in tags:
                if tag in self.de_tag:
                    flag = 1
                    break
            if flag:
                continue
            # get src_url
            src_list.append(img_obj.img['src'])

        return src_list

    # save image to local // check size
    def save_img(self, src_list, header={},
                 p_exp=re.compile('(\.[a-zA-Z]+?)\?'), p_id=re.compile('\?([0-9]+)')):
        logging.info('save images...')
        for src in src_list:
            url = 'http:' + src
            img = requests.get(url, headers=header, timeout=15)
            # get expand name
            exp_name = p_exp.search(src).groups()[0]
            # get id
            pid = p_id.search(src).groups()[0]
            # save origin
            filename = self.dir_origin + pid + exp_name
            with open(filename, 'wb') as f:
                f.write(img.content)

            # check size
            data = cv2.imdecode(np.frombuffer(img.content, dtype=np.uint8), 3)
            try:
                high = data.shape[0]
                width = data.shape[1]
            except AttributeError:
                continue
            if high > width*1.5 or width > high*1.5:
                logging.debug('image ignored!')
                continue
            else:
                # save cut
                data = self.img_cut(data)
                filename = self.dir_filter + pid + '.jpg'
                cv2.imwrite(filename, data)
        logging.info('save images over')
        return 1

    # get a np.array, return a np.array
    def img_cut(self, data):
        high = data.shape[0]
        width = data.shape[1]
        if high > width:
            start = int(high/2.0 - width/3.0)
            data = data[start: start+width, ]
        elif high < width:
            start = int(width/2.0 - high/2.0)
            data = data[:, start: start+high]

        if data.shape[0] > self.size:
            cv2.reszie(data, (150, 150))
        return data

    def get_max_pid(self, p=re.compile('pid=([0-9]+)')):
        page = requests.get(self.page_now, headers=self.header, timeout=15)
        soup = BeautifulSoup(page.text, 'lxml')
        a = soup.find(alt='last page')
        pid_max = p.search(a['href']).groups()[0]
        return int(pid_max)

    def run(self):
        pid_max = self.get_max_pid()
        logging.info("will get %d pages, max_pid = %d" % (self.page, pid_max))
        for i in range(self.page):
            logging.info('get page %d' % i)
            if self.pid_now + i*self.count > pid_max:
                logging.warning('get page of max-pid! now: max:')
                break

            soup = self.get_next_page()
            src_list = self.parse_page(soup)
            self.save_img(src_list)


#######################################
# run

if __name__ == "__main__":
    sp = Spider()
    sp.run()

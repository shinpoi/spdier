# - coding: utf-8 -*-
# python 3.5
# first spider

import os
import requests
import json
import time
import logging
import re
from bs4 import BeautifulSoup


ID = "---------"
PW = "---------"
pwd = os.path.dirname(__file__) + '/'

try:
    with open(pwd + 'kfol_cookies_' + ID + '.json', 'r') as f:
        COOKIES = requests.utils.cookiejar_from_dict(json.loads(f.read()))
except IOError:
    COOKIES = None

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename=pwd + 'kfol_log_' + ID + '.log',
                    filemode='a'
                    )


class KfOl(object):
    def __init__(self, id, password, cookies):
        self.url = 'http://bbs.2dkf.com/'
        self.url_login = 'http://bbs.2dkf.com/login.php'
        self.url_homepage = 'http://bbs.2dkf.com/index.php'
        self.url_kfol = 'http://bbs.2dkf.com/kf_fw_ig_index.php'
        self.url_kfol_click = 'http://bbs.2dkf.com/kf_fw_ig_intel.php'
        self.url_growup = 'http://bbs.2dkf.com/kf_growup.php'
        self.pwd = os.path.dirname(__file__) + '/'

        self.id = id
        self.password = password
        self.cookies = cookies
        self.safeid = {'safeid': ''}

        self.login_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "123",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "bbs.2dkf.com",
            "Origin": "http://bbs.2dkf.com",
            "Referer": "http://bbs.2dkf.com/index.php",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36"
        }

        self.login_data = {
            "jumpurl": "index.php",
            "step": "2",
            "lgt": "1",
            "hideid": "1",
            "cktime": "31536000",
            "pwuser": id.encode('gbk'),
            "pwpwd": password,
            "submit": "登陆".encode('gbk')
        }

        self.get_header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2",
            "Connection": "keep-alive",
            "Host": "bbs.2dkf.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36"
        }

        self.kfol_header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2",
            "Connection": "keep-alive",
            "Content-Length": "14",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "bbs.2dkf.com",
            "Origin": "http://bbs.2dkf.com",
            "Referer": "http://bbs.2dkf.com/kf_fw_ig_index.php",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def get_safeid(self, soup):
        script = str(soup.find_all('script'))
        pattern = re.compile('safeid=[a-zA-Z0-9]+')
        sid = re.search(pattern, script).group()
        sid = sid.split('=')
        self.safeid['safeid'] = sid[1]

    def update_cookies(self, new_cookies):
        origin = requests.utils.dict_from_cookiejar(self.cookies)
        neo = requests.utils.dict_from_cookiejar(new_cookies)
        for i in neo:
            origin[i] = neo[i]
        self.cookies = requests.utils.cookiejar_from_dict(origin)
        logging.info('update cookies')

    def is_login(self, soup):
        soup = soup.find(class_="topright")
        soup = soup.find('a')
        return soup.text == self.id

    def login(self):
        r = requests.post(self.url_login, data=self.login_data, headers=self.login_header, cookies=self.cookies)
        self.cookies = r.cookies

    def kfol(self):
        r = requests.post(self.url_kfol_click, data=self.safeid, headers=self.kfol_header, cookies=self.cookies)
        logging.info('attack0')
        while r.text:
            time.sleep(1.5)
            logging.info('attack!')
            r = requests.post(self.url_kfol_click, data=self.safeid, headers=self.kfol_header, cookies=self.cookies)
        logging.info('kfol end')

    def get_reward(self):
        r = requests.get(self.url_growup, headers=self.get_header, cookies=self.cookies)
        self.update_cookies(r.cookies)

        soup = BeautifulSoup(r.text, 'html5lib')
        a = soup.find(target='_self')
        try:
            url_reward = self.url + a['href']
            requests.get(url_reward, headers=self.get_header, cookies=self.cookies)
        except:
            pass

    def run(self):
        # get homepage and check if login
        r = requests.get(self.url_homepage, headers=self.get_header, cookies=self.cookies)
        soup = BeautifulSoup(r.text, 'html5lib')

        if self.is_login(soup):
            logging.info('success login by local-cookies!')
        else:
            for i in range(3):
                self.login()
                r = requests.get(self.url_homepage, headers=self.get_header, cookies=self.cookies)
                soup = BeautifulSoup(r.text, 'html5lib')

                if self.is_login(soup):
                    logging.info('success login by login.php!')
                    break
                else:
                    logging.error('login failed! at %d times' % i)
                    time.sleep(60)

        # get page of kfol
        r = requests.get(self.url_kfol, headers=self.get_header, cookies=self.cookies)
        self.update_cookies(r.cookies)

        # get_safeid
        soup = BeautifulSoup(r.text)
        self.get_safeid(soup)

        logging.info('kfol start')
        self.kfol()

        # get page of daily-reward
        self.get_reward()

        # save cookies
        json_cookies = requests.utils.dict_from_cookiejar(self.cookies)
        with open(self.pwd + 'kfol_cookies_' + self.id + '.json', 'w') as f:
            f.write(json.dumps(json_cookies))
        logging.info('cookies saved')


# run
spider = KfOl(ID, PW, COOKIES)
spider.run()

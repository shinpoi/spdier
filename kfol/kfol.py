# - coding: utf-8 -*-
# python 3.4+

import os
import sys
import requests as rq
import time

import json
import time
import logging
import re
from bs4 import BeautifulSoup

ID = None
PW = None


PWD = os.path.abspath(sys.argv[0])
PWD = re.compile('[^/]+\.py$').sub('', PWD)[:-1]
# if not PWD:
#    PWD = '/tmp'

with open(PWD + '/kfol_user.json') as f:
    j = json.loads(f.read())
    ID = j['id']
    PW = j['pw']

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename=PWD + '/kfol_log_' + ID + '.log',
                    filemode='a'
                    )
LOG = logging.root.getChild('kfol')

WAIT_SECONDS = 1
HOST = 'bbs.ikfol.com'
# HOST = 'bbs.9moe.com'
URL_HOST = 'https://' + HOST
URL_HP = URL_HOST + '/index.php'
URL_KFOL = URL_HOST + '/kf_fw_ig_index.php'
URL_DAILY_REWARD = URL_HOST + '/kf_growup.php'
URL_ITEM_LIST = URL_HOST + '/kf_fw_ig_mybp.php'

ENDPOINT_LOGIN = URL_HOST + '/login.php?'
ENDPOINT_KFOL_CLICK = URL_HOST + '/kf_fw_ig_intel.php'
ENDPOINT_USE_ITEM = URL_HOST + '/kf_fw_ig_mybpdt.php'

DEFAULT_HEADER = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Connection": "keep-alive",
    "Host": HOST,
    "Origin": URL_HOST,
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Aoi-lucario/KFOLer/v0.2"
}

# {item_name: limit}
ITEMS = {"蕾米莉亚同人漫画": 50,
         "十六夜同人漫画": 50,
         "档案室钥匙": 30,
         "傲娇LOLI娇蛮音CD": 30,
         "消逝之药": 10,
         "整形优惠卷": 10}

try:
    with open(PWD + '/kfol_cookies_' + ID + '.json', 'r') as f:
        COOKIES = rq.utils.cookiejar_from_dict(json.loads(f.read()))
except IOError:
    COOKIES = {}


def ignore_error(func):
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception as e:
            LOG.exception(e)
            return None

    return wrapper


class KFClient:
    def __init__(self, uid=ID, pw=PW, session=None):
        if not (uid and pw):
            raise ValueError('not get id or password !')

        self.uid = uid
        self.pw = pw
        self.safeid = None

        if not session:
            self.session = rq.Session()
        else:
            self.session = session
        self.session.headers.update(DEFAULT_HEADER)
        self.session.cookies.update(COOKIES)
        self.session.verify = False

    def is_login(self):
        res = self.session.get(URL_HP)
        self.session.cookies.update(res.cookies)

        islogin = self.uid in res.text
        if islogin:
            self.set_safeid(res)
        return islogin

    def set_safeid(self, response):
        pattern = re.compile('safeid=([a-zA-Z0-9]+)')
        self.safeid = pattern.search(response.text).group(1)

    def login(self):
        if self.is_login():
            LOG.info('use exist cookies')
            return

        LOG.info('no local cookies or cookies expired, login...')
        # TODO: parse form instead fixed login data
        login_data = {
            "forward": "",
            "jumpurl": "https://bbs.2dkf.com/profile.php?action=favor",
            "step": "2",
            "lgt": "1",
            "hideid": "0",
            "cktime": "31536000",
            "pwuser": self.uid.encode('gbk'),
            "pwpwd": self.pw,
            "submit": "登陆".encode('gbk')
        }
        ex_header = {"Content-Type": "application/x-www-form-urlencoded", "Referer": URL_HP}

        # retry 5 times
        count = 1
        while count < 5:
            res = self.session.post(ENDPOINT_LOGIN, data=login_data, headers=ex_header)
            self.session.cookies.update(res.cookies)
            time.sleep(WAIT_SECONDS)
            if self.is_login():
                return
            count += 1
            time.sleep(10)
            LOG.warning('login failed! try %d/5' % count)
        raise ValueError('login failed 5 times!')

    def dump_cookies(self, filepath=None):
        json_cookies = rq.utils.dict_from_cookiejar(self.session.cookies)
        if not filepath:
            filepath = PWD + '/kfol_cookies_' + self.uid + '.json'
        logging.info('dump cookies to ' + filepath)
        with open(filepath, 'w') as jf:
            jf.write(json.dumps(json_cookies))

    @ignore_error
    def fight(self):
        """
        TODO: log fight log, max level, etc...
        """
        ex_header = {"Referer": URL_KFOL,
                     "X-Requested-With": "XMLHttpRequest"'https://bbs.2dkf.com/login.php'}
        res = 'foobar'
        count = 0
        limit = 500
        while res and res != 'no' and count < limit:
            LOG.debug('attack!')
            r = self.session.post(ENDPOINT_KFOL_CLICK, data={'safeid': self.safeid}, headers=ex_header)
            res = r.text
            count += 1
            time.sleep(WAIT_SECONDS)
        if count >= limit:
            # should be not arrive here
            LOG.error('fight over %d times ..?' % limit)

    @ignore_error
    def handle_boxs(self):
        box_limit = 500
        for i in range(1, 5):
            for j in range(box_limit):
                time.sleep(WAIT_SECONDS)
                r = self.session.post(ENDPOINT_USE_ITEM, data={'do': 3, 'id': i, 'safeid': self.safeid})
                LOG.debug(r.text)
                # TODO: bad condition...
                if r.text == '盒子不足，请刷新查看最新数目。':
                    break

    @ignore_error
    def handle_items(self):
        # TODO: fix this function
        res = self.session.get(URL_ITEM_LIST)
        soup = BeautifulSoup(res.text, 'lxml')
        tb_items = soup.find_all('tr', id=re.compile('wp_[0-9]+'))
        items_id = [tb['id'].replace('wp_', '') for tb in tb_items]
        for item_id in items_id:
            time.sleep(1.5)
            # sell item
            data = {'do': 2, 'id': item_id, 'safeid': self.safeid}
            # use item
            # TODO: should be refresh list after used item
            # data = {'do': 1, 'id': item_id, 'safeid': self.safeid}
            self.session.post(ENDPOINT_USE_ITEM, data=data)

    @ignore_error
    def handle_weapons(self):
        p = re.compile('wp_([0-9]+)')
        for i in range(5):
            time.sleep(WAIT_SECONDS)
            res = self.session.get(URL_ITEM_LIST)
            soup = BeautifulSoup(res.text, 'lxml')
            table = soup.find(class_='kf_fw_ig4')
            weapons = table.find_all(id=p)
            n = 0
            for weapon in weapons:
                time.sleep(WAIT_SECONDS)
                if '神秘' in weapon.parent.text:
                    n += 1
                else:
                    id_ = p.match(weapon['id']).group(1)
                    # smelt weapons
                    self.session.post(ENDPOINT_USE_ITEM, data={'do': 5, 'id': id_, 'safeid': self.safeid})
            # no more page
            # TODO: change condition
            if n == len(weapons):
                break

    @ignore_error
    def get_daily_reward(self):
        r = self.session.get(URL_DAILY_REWARD)
        soup = BeautifulSoup(r.text, 'lxml')
        a = soup.find(target='_self')
        time.sleep(WAIT_SECONDS)
        url_reward = URL_HOST + "/" + a['href']
        self.session.get(url_reward)

    def kfol_start(self):
        LOG.info('---------- try login ----------')
        self.login()

        LOG.info('---------- kfol start ----------')
        # init kfol cookies
        r = self.session.get(URL_KFOL)
        self.session.cookies.update(r.cookies)

        LOG.info('start fight')
        self.fight()

        LOG.info('start handle box')
        self.handle_boxs()

        LOG.info('start handle items')
        self.handle_items()

        LOG.info('start handle weapons')
        self.handle_weapons()

        LOG.info('start get daily reward')
        self.get_daily_reward()
        LOG.info('---------- kfol end ----------')

        self.dump_cookies()


# run
if __name__ == '__main__':
    client = KFClient(ID, PW)
    client.kfol_start()

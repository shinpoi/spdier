# -*- coding: utf-8 -*-
# python 2.7

import os
import requests
import json
import time
import datetime
import logging
import re
from bs4 import BeautifulSoup
import sys
# import setting

# Set encode: utf-8
reload(sys)
sys.setdefaultencoding('utf8')

# Parameter
ID = "Your ID"
PW = "Your Password"

SAVE_PATH = os.path.dirname(__file__) + '/'
LOG_LEVEL = logging.INFO
LOG_TO_CONSOLE = True

# Set logging
try:
    os.mkdir(SAVE_PATH + 'log/')
except OSError:
    pass

logging.basicConfig(level=LOG_LEVEL, # level=setting.LOG_LEVEL,
                    format='[%(levelname)s]   \t %(asctime)s \t%(message)s\t',
                    datefmt='%Y/%m/%d (%A) - %H:%M:%S',
                    filename=SAVE_PATH + 'log/' + 'PixivCrawler_' + time.strftime('%Y-%m-%d_%H-%M') + '.log',
                    # filename=setting.LOG_DIR + 'Crawler_' + time.strftime('%Y-%m-%d_%H-%M') + '.log',
                    filemode='a'
                    )

# if setting.TO_CONSOLE:
if LOG_TO_CONSOLE:
    console = logging.StreamHandler()
    console.setLevel(LOG_LEVEL)  # setting.LOG_LEVEL
    formatter = logging.Formatter('[%(levelname)s]  \t%(message)s\t')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

# Yesterday
today = datetime.date.today()
if int(time.strftime('%H')) < 10:
    oneday = datetime.timedelta(days=2)
else:
    oneday = datetime.timedelta(days=1)
yesterday = today-oneday

DATE = yesterday.strftime('%Y%m%d')


class Crawler(object):
    def __init__(self, user, pw, date, save_path):
        self.id = user
        self.pw = pw
        self.uid = ''
        self.path = save_path
        self.times = date

        self.domain = 'www.pixiv.net'
        self.homepage = 'http://www.pixiv.net/'
        self.pre_login_page = 'https://accounts.pixiv.net/login?lang=en&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.login_page = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.image_page = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id='
        self.manga_page = 'http://www.pixiv.net/member_illust.php?mode=manga&illust_id='
        self.score_page = 'http://www.pixiv.net/rpc_rating.php'
        self.ranking_page = 'http://www.pixiv.net/ranking.php?'
        self.works_page = 'http://www.pixiv.net/member_illust.php?type=all&id='
        self.bookmarks_page = 'http://www.pixiv.net/bookmark.php?rest=show&id='

        self.headers_base = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': self.homepage,
        }

        self.pattern_host = re.compile('https?://(.+?)/')
        self.pattern_tt = re.compile('pixiv.context.token = "([a-zA-Z0-9]+?)";')
        self.pattern_uid = re.compile('id=([0-9]+)')

        self.cookies = self.load_cookies()

    @staticmethod
    # Need bit data of image.
    def classifiter(data):
        # img = cv2.imdecode(np.asarray(bytearray(data), dtype=np.uint8), 0)
        return True

    # Load cookies from file. | Success: read cookies ; False: login and get new cookies.
    def load_cookies(self):
        try:
            with open(self.path + 'cookies.json', 'r') as f:
                cookies = requests.utils.cookiejar_from_dict(json.loads(f.read()))
            logging.info('read cookies')
            cookies = self.check_cookies(cookies)

            # check dose cookies is overdue
            if cookies:
                pass
            else:
                logging.warning('Cookies is overdue!')
                cookies = self.login()

        except IOError:
            logging.warning("Didn't find cookies")
            cookies = self.login()

        return cookies

    # Save cookies into file.
    def save_cookies(self, cookies):
        cookies = requests.utils.dict_from_cookiejar(cookies)
        with open(self.path + 'cookies.json', 'w') as f:
            f.write(json.dumps(cookies))
        logging.info('cookies was saved')

    # Save data into file. (Need name includes relativepath)
    def save_file(self, name, src):
        if not src:
            logging.error("save_file(): Did't get data")
            return False
        with open(self.path + name, 'wb') as f:
            f.write(src)
        logging.info('File %s saved' % self.path + name)

    @staticmethod
    # Update cookies. | Success:  updated cookies;
    def update_cookies(old_cookies, new_cookies):
        origin = requests.utils.dict_from_cookiejar(old_cookies)
        neo = requests.utils.dict_from_cookiejar(new_cookies)
        for i in neo:
            origin[i] = neo[i]
        neo = requests.utils.cookiejar_from_dict(origin)
        logging.info('update cookies')
        return neo

    # Check cookies by access homepage. | Success: cookies ; False: False(bool)
    def check_cookies(self, cookies):
        # Get Homepage
        logging.info('access homepage')
        headers = self.headers_base
        headers['Host'] = self.domain
        time.sleep(1)

        r = requests.get(self.homepage, headers=headers, cookies=cookies)
        soup = BeautifulSoup(r.text, 'lxml')
        check_id = soup.find('h1', class_='user')
        if not check_id:
            logging.error('Can not get uid from homepage')
            return False

        if check_id.text == self.id:
            # Set uid
            uid = soup.find('a', class_='user-link')['href']
            self.uid = re.search(self.pattern_uid, uid).group(1)
            new_cookies = self.update_cookies(cookies, r.cookies)
            self.save_cookies(new_cookies)
            return new_cookies
        else:
            return False

    # Login and get new cookies. | Success: new cookies ; False: raise ValueError (and break program)
    def login(self):
        # Pre-Login
        logging.info('Login Pixiv ...')
        r = requests.get(self.pre_login_page)
        logging.info('Pre-Login... status_code: %s' % r.status_code)
        cookies = r.cookies
        headers = self.headers_base
        soup = BeautifulSoup(r.text, 'lxml')

        # Login
        headers['Referer'] = self.pre_login_page
        headers['Host'] = re.search(self.pattern_host, self.login_page).group(1)

        f = soup.find("form", action="/login")
        post_data = {}
        for i in f.find_all('input'):
            try:
                post_data[i['name']] = i['value']
            except KeyError:
                post_data[i['name']] = ''
        post_data['pixiv_id'] = self.id
        post_data['password'] = self.pw

        r = requests.post(self.login_page, data=post_data, headers=headers, cookies=cookies)
        logging.info('Login... status_code: %s' % r.status_code)
        time.sleep(1)
        cookies = self.check_cookies(r.cookies)
        if cookies:
            logging.info("Login successful. ID = %s " % self.id)
        else:
            logging.error("Login Failed! ID = %s " % self.id)
            raise ValueError
        return cookies

    @staticmethod
    def image_format(url):
        pattern_img_url = re.compile('/[0-9]+_p[0-9]+.(jpg|gif|png|bmp)')
        name = re.search(pattern_img_url, url).group(0)
        img_format = re.search(pattern_img_url, url).group(1)
        return name[1:], img_format

    # Get original image by image_id. | Success(illust): ((name, format, data), )  <--tuple ;
    #                                   Success(manga): [(name 1, format 1, data 1), (name 2, format 2, data 2), ...)] <--list ;
    #                                   False: None
    def get_images_by_id(self, img_id, referer=None):
        # get url of original image
        url = self.image_page + img_id
        headers = self.headers_base
        if referer:
            headers['Referer'] = referer
        headers['Host'] = self.domain

        # access medium image page
        r = requests.get(url, headers=headers, cookies=self.cookies)
        soup = BeautifulSoup(r.text, 'lxml')

        # illust
        # get url of original image
        img_url = soup.find('img', class_='original-image')
        if img_url:
            img_url = img_url['data-src']
            # get original image
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
                'Referer': url
            }

            name, img_format = self.image_format(img_url)

            # .GTF files will be dealt with next Version (Maybe... #1
            if img_format == 'gif':
                return None
            img = requests.get(img_url, headers=headers)
            return (name, img_format, img.content),

        # manga
        manga = soup.find('div', class_='multiple')
        if manga:
            img_url = self.manga_page + img_id

            # access manga page
            r = requests.get(img_url, headers=headers, cookies=self.cookies)
            soup = BeautifulSoup(r.text, 'lxml')

            # get list of img
            tag_list = soup.find_all('img', class_='image')
            page = len(tag_list)

            # If a image-id has more than 10 images,  ignored it.
            if page > 10:
                logging.info('Ignored id: %s (too more image)' % img_id)
                return None

            # get original image
            headers['Referer'] = img_url
            manga_page = "http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=" + img_id + "&page="
            img_list = []
            for i in range(page):
                # get url of original image
                url = manga_page + str(i)
                r = requests.get(url, headers=headers, cookies=self.cookies)
                soup = BeautifulSoup(r.text, 'lxml')
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
                    'Referer': url
                }

                url = soup.find('img')['src']

                # get original image
                name, img_format = self.image_format(url)
                # .GTF files will be dealt with next Version (Maybe... #2
                if img_format == 'gif':
                    return None
                img = requests.get(url, headers=headers)
                img_list.append((name, img_format, img.content))
            return img_list

        return None

    # Score image by image_id.
    def score(self, img_id, tt, score='10'):
        url = self.image_page + img_id
        headers = self.headers_base
        headers['Referer'] = url
        headers['Host'] = self.domain

        data = {
            'mode': 'save',
            'i_id': img_id,
            'u_id': self.uid,
            'qr': '0',
            'score': score,
            'tt': tt,
        }

        r = requests.post(self.score_page, data=data, headers=headers, cookies=self.cookies)
        try:
            res = json.loads(r.text)
            if res['re_sess']:
                logging.info('Score image(id=%s) by %s' % (img_id, score))
            else:
                logging.warning('Score image(id=%s) failed \t\n response: %s' % (img_id, r.text))
        except ValueError:
            logging.error('Score image(id=%s) failed (didn\'t get response)' % img_id)

    # Collect image's id-list of ranking. | Success: id-list ;
    def scan_ranking(self, mode='daily', content='illust', page=4, date=''):
        if date:
            pass
        else:
            date = self.times

        logging.info('Start scan ranking.(mode=%s, content=%s, date=%s)' % (mode, content, date))

        overview_url = self.ranking_page + 'mode=' + mode + '&content=' + content + '&date=' + date
        headers = self.headers_base
        headers['Referer'] = self.homepage
        headers['Host'] = self.domain
        r = requests.get(overview_url, headers=headers, cookies=self.cookies)
        tt = re.search(self.pattern_tt, r.text).group(1)

        id_list = set()
        for i in range(page):
            para = 'mode=' + mode + '&content=' + content + '&date=' + date + '&p=' + str(i+1) + '&format=json&tt=' + tt
            json_url = self.ranking_page + para
            json_rank = json.loads(requests.get(json_url, headers=headers, cookies=self.cookies).text)
            try:
                for img_json in json_rank['contents']:
                    id_list.add(str(img_json['illust_id']))
                time.sleep(0.5)
            except KeyError:
                print(json_rank)
                logging.error('Get json of page %s failed' % str(i+1))

        logging.info('End scan ranking.')
        return id_list

    # Collect image's id-list of artist's works/bookmarks. | Success: id-list ;
    def scan_artist(self, uid, class_='works'):
        logging.info('Start scan user(id=%s), scan_type is: %s.' % (uid, class_))

        if class_ == 'works':
            page = self.works_page
        elif class_ == 'bookmarks':
            page = self.bookmarks_page
        else:
            logging.error('scan_artist(): Get a wrong value of class_: %s' % class_)
            raise ValueError

        headers = self.headers_base
        headers['Host'] = self.domain
        max_page = '0'
        new_max_page = '1'

        while max_page != new_max_page:
            max_page = new_max_page
            url = page + uid + '&p=' + max_page
            r = requests.get(url, headers=headers, cookies=self.cookies)
            soup = BeautifulSoup(r.text, 'lxml')
            new_max_page = soup.find('ul', class_='page-list')
            if new_max_page:
                new_max_page = new_max_page.find_all('li')[-1].text
            else:
                new_max_page = '1'
                break

        logging.info('Has %s pages!' % new_max_page)
        id_list = []
        for i in range(int(max_page)):
            url = page + uid + '&p=' + str(i+1)
            r = requests.get(url, headers=headers, cookies=self.cookies)
            soup = BeautifulSoup(r.text, 'lxml')
            tag_list = soup.find_all('img', class_='ui-scroll-view')
            for tag in tag_list:
                id_list.append(tag['data-id'])
            time.sleep(0.5)

        logging.info('End scan user')
        return id_list

    def crawler(self, id_list, save_file):
        try:
            os.mkdir(save_file)
        except OSError:
            pass

        logging.info('Start for write image in %s' % save_file)
        num = str(len(id_list))
        n = 0
        for img_id in id_list:
            n += 1
            logging.info("check image %s/%s" % (str(n), num))
            images_p = self.get_images_by_id(img_id)

            if images_p:
                for image in images_p:
                    if self.classifiter(image[2]):
                        with open(save_file + image[0], 'wb') as f:
                            f.write(image[2])
                            logging.info('wrote image: %s' % image[0])
                    else:
                        logging.info('Ignored image: %s' % image[0])
                time.sleep(0.5)
            else:
                logging.info('Ignored id: %s' % img_id)
        logging.info('End for write image in %s' % save_file)

    def craw(self):
        # check daily ranking (rank=200)
        id_list = self.scan_ranking()
        file_name = self.path + 'Daily_Rank_' + self.times + '_' + str(len(id_list)) + 'p/'
        self.crawler(id_list=id_list, save_file=file_name)

        # check works of artist (ポコ(id=76266))
        id_list = self.scan_artist(uid='76266')
        file_name = self.path + 'ポコ(76266)_works' + '_' + str(len(id_list)) + 'p/'
        self.crawler(id_list=id_list, save_file=file_name)

        # check bookmarks of me (aqueous002(id=1941321))
        id_list = self.scan_artist(uid='1941321', class_='bookmarks')
        file_name = self.path + 'aqueous002(1941321)_bookmarks' + '_' + str(len(id_list)) + 'p/'
        self.crawler(id_list=id_list, save_file=file_name)

        self.check_cookies(self.cookies)


c = Crawler(user=ID, pw=PW, date=DATE, save_path=SAVE_PATH)
c.craw()

"""
except Exception, er:
    logging.error('Crawler(): Get error: %s' % er)
    raise ValueError
"""
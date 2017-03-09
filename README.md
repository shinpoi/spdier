# spdier
net-spider write by Python 3.5  
just for fun ^_^

* need library:  
[urllib3](https://urllib3.readthedocs.io/en/latest/): `pip3 install urllib3`  
[requests](http://docs.python-requests.org/en/master/): `pip3 install requests`  
[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): `pip3 install beautifulsoup4 html5lib`  
(If you used CentOS and want use lxml, maybe you should `yum install libxml2-devel libxslt-devel`, `pip3 install lxml`)  

***

## osen.py

Spider for net-drama [Osen](http://www.onsen.ag/program/home/)  

When runing this program, it would check the count of issue in `id_list`, if has a new issue, program wil download the new audio file and update info file.

* Log file would be builed on the same path of `osen.py`.  
* Edit `save_path` to change where the audio files and infos file are saved in.  
* **Need combine with cron tools like [crontab](http://www.computerhope.com/unix/ucrontab.htm) to use**

example:  
`crontab -e`  
then:  
`30 1 * * * <absolute path of your python3> <absolute path of osen.py>`  

***
*Thanks: Thanks for Guo of YTS for his technical support!*  

***

## kfol.py

Play kfol and get dayly-reward automaticly. (But need distributing status point by yourself.)  
Just edit `ID = '...'` and `PW = '...'`

* **Need combine with cron tools like [crontab](http://www.computerhope.com/unix/ucrontab.htm) to auto play everday.**

***

## pixiv_crawler.py

A web-crawler can scan and download image from [pixiv](http://www.pixiv.net).

* If you want use this script at *Python2.7*, just do:
```
- #reload(sys)
- #sys.setdefaultencoding('utf8')

+ reload(sys)
+ sys.setdefaultencoding('utf8')
```

Change `ID = "Your ID"`and `PW = "Your Password"` to your own account & password.

**Images, logs and cookies will be saved in the same directory of pixiv_crawler.py.**  
Edit `SAVE_PATH = './'` to change it.

* Method of `Crawler.craw()` just a test. **Expand it by what your need.**  
  * What `Crawler.craw()` do ?  
    1.Download the first 200 rank of daily ranking. If a image-id has more than 10 pictures, it will be ignored.  
    2.Download all of works of user '76266'([ポコ](http://www.pixiv.net/member.php?id=76266)).  
    3.Download all of bookmarks of me (1941321).  
    
* Now this crawler has two main method:  
  * **def scan_ranking(mode=**'daily', **content=**'illust', **page=**4**)**:  
    `mode:` 'daily', 'weekly', 'monthly', 'rookie', 'original', 'male', 'female'.  
    `page:` 50 images per page.  
  * **def scan_artist(uid**, **class_=**'works'**)**:  
    `uid`: artist's uid.  
    `class_=`: 'works' or 'bookmarks'  

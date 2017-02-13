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

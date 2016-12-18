# spdier
net-spider write by Python 3.5  
just for fun

* need library:  
[urllib3](https://urllib3.readthedocs.io/en/latest/): `pip3 install urllib3 `  
[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): `pip3 install beautifulsoup4 html5lib`  

***
>**osen.py**  

Spider for [Osen](http://www.onsen.ag/program/home/)  
Download "ほめらじ" every issue.  

Awake every 60min, and check time of system.  
If Hour == 23, then gather information form homepage of Osen.  
If find new issue, download the audio file to `save_path ` and update `info_file_name`  
`(Ok, of course I konw homeraji will be updated at every thursday ...`


***
*Thanks: Thanks for Guo of YTS for his technical support!*  

P.S.不要吐槽我丑陋的英语……当然，有错误请务必指出（众: 哪都是错

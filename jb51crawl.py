#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/9 16:45
# @Author  : GUILIN
# @Site    : 
# @File    : jb51crawl.py
# @Software: PyCharm

import requests
from fake_useragent import UserAgent
from lxml import etree
import MySQLdb

def output_db(table_name,data):
    db = MySQLdb.connect('localhost', 'root', 'abc14102c', 'spider', charset="utf8")
    cursor = db.cursor()

    sql='''create table if not exists jb51book (
    title varchar(100) NOT NULL,
    star varchar(10) NOT NULL,
    detailurl varchar(100) NOT NULL,
    image varchar(100) NOT NULL,
    cata varchar(10) NOT NULL,
    msize varchar(10) NOT NULL,
    pubdate varchar(10) NOT NULL,
    describer varchar(400) NOT NULL,
    downloadlink varchar(100) NOT NULL,
    sharecode varchar(10) NOT NULL
    ) DEFAULT CHARSET=utf8
    '''

    cursor.execute(sql)
    db.commit()
    if data is None:
        print('没有数据')
        return
    cursor.execute(
        'INSERT INTO %s (title, star, detailurl, image, cata, msize, pubdate, describer, downloadlink, sharecode) values %s' % (
        table_name,data))
    db.commit()

def crawl(url):
    baseurl = 'https://www.jb51.net'
    ua = UserAgent(verify_ssl=False)
    headers = {'UserAgent': ua.random}
    res = requests.get(url, headers=headers)
    res.encoding = 'gbk'  # 重要
    et = etree.HTML(res.text)
    booklist = et.xpath('//*[@id="list_ul_more"]/li')

    for i in range(1,len(booklist)+1):
        title=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[1]/p/a/text()'.format(i))[0]
        star=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[1]/span/i/@class'.format(i))[0][-1:]
        detaillink=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[1]/p/a/@href'.format(i))[0]
        detailurl=baseurl+detaillink
        try:
            image=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[2]/div[1]/div[1]/a/div/img/@src'.format(i))[0]
        except:
            image='none'
        cata=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[2]/div[1]/div[2]/p[1]/span[1]/a/text()'.format(i))[0]
        msize=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[2]/div[1]/div[2]/p[1]/span[2]/text()'.format(i))[0]
        pubdate=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[2]/div[1]/div[2]/p[1]/span[3]/text()'.format(i))[0]
        describer=et.xpath('//*[@id="list_ul_more"]/li[{}]/div[2]/div[1]/div[2]/p[2]/text()'.format(i))[0]
        detailres=requests.get(detailurl,headers=headers)
        try:
            downloadlink=etree.HTML(detailres.text).xpath('//*[@id="download"]/ul/li[1]/ul[2]/li[1]/a/@href')[0][0:100]
        except:
            downloadlink='none'
        sharecode=detaillink[7:13]
        data=(title, star, detailurl, image, cata, msize, pubdate, describer, downloadlink, sharecode)
        print(data)
        output_db('jb51book',data)

if __name__ == '__main__':
    # urls = [ 'https://www.jb51.net/books/list476_{}.html'.format(i) for i in range(1, 14) ]  # python电子书，自动根据规则生成要爬取的地址库
    urls=['https://www.jb51.net/books/list509_{}.html'.format(i) for i in range(1,45)] #其他编程书
    for url in urls:
        print('start crawl page:', url)
        crawl(url)
    print('end crawl.....')
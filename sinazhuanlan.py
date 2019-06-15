#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/15 12:33
# @Author  : GUILIN
# @Site    : 
# @File    : sinazhuanlan.py
# @Software: PyCharm
'''
基本思路
1、get_page通过url获取json文件
2、parser_page 解析json，获取文章列表
3、get_article_content根据文章内容地址解析获取具体文章内容
4、save_article 文章内容保存至文件或数据库
'''

import requests
from urllib.parse import urlencode
import pysnooper
from fake_useragent import UserAgent
import re
import json
from lxml import etree
import MySQLdb

# @pysnooper.snoop()
#获取网页内容
def get_page(page):
    baseurl='http://interface.sina.cn/finance/api_feed.d.json?'
    params={
        'cid':56446,
        'callback':'jQuery110208176347882510322_1560581169997',
        'page':page,
        'size':20,
    }
    url=baseurl+urlencode(params)
    ua=UserAgent(verify_ssl=False)
    headers={'headers':ua.random}
    try:
        res=requests.get(url,headers=headers)

        if res.status_code==200:
            '''
            re正则方式提取（）中字符。
            r 表示字符串为非转义的原始字符串，让编译器忽略反斜杠，也就是忽略转义字符。
            []用来表示一组字符
            .通配符,可以表示任意字符
            * 匹配0至无穷次的字符
            加？,实现惰性匹配(只匹配最少的)
            re.S 即为 . 并且包括换行符在内的任意字符（. 不包括换行符）
            '''
            res = res.text
            p = re.compile(r'[(](.*)[)]', re.S)
            res=re.findall(p,res)
            res=res[0]
            jsonobj=json.loads(res)
            return jsonobj

    except requests.ConnectionError as e:
        return None

# @pysnooper.snoop()
#解析生成文章list
def paraser_page(content):

    articles=content['result']['data']['articles']
    for article in articles:
        author_name=article.get('author_name')
        title=article.get('title')
        summary=article.get('summary')
        publish_time=article.get('publish_time')
        pub_url=article.get('pub_url')
        articlecontent=get_article_content(pub_url)
        yield {
            'title':title,
            'author_name':author_name,
            'summary':summary,
            'publish_time':publish_time,
            'articlecontent':articlecontent,
        }

#获取文章详细内容
def get_article_content(articleurl):
    res1 = requests.get(articleurl)
    res1.encoding = 'utf-8'
    et = etree.HTML(res1.text)
    content0 = et.xpath('//*[@id="artibody"]//p/text()')#list
    content1='\n'.join(content0)#list转化为str
    content1=content1.replace('\u3000',' ')#删除文章中的\u3000空格
    return content1

# @pysnooper.snoop()
#保存到本地文件
def save_article_txt(item):
    with open(r'C:\Users\guili\Desktop\data.txt','a+',encoding='utf-8') as f:#需要使用encoding=utf8，python写txt默认编码为gbk
        for value in item.values():
            f.write(value+'\t')
        f.write('\n')
    f.close()
@pysnooper.snoop()
#保存到mysql
def save_article_mysql(item):
    con=MySQLdb.connect('localhost','root','abc14102c','spider',charset='utf8mb4')#
    cur=con.cursor()
    data=(item["title"],item["author_name"],item["summary"],item["publish_time"],item["articlecontent"])
    print(data)
    insertsql='INSERT INTO SINAZL (title,author_name,summary_article,publish_time,article_content) VALUES (%s,%s,%s,%s,%s)'
    try:
        cur.execute(insertsql,data)
        con.commit()
    except:
        con.rollback()
        print('sql fail')
    con.close()

# @pysnooper.snoop()
def main():
    for page in range(1,10):
        content=get_page(page)
        m=paraser_page(content)
        for item in m:
            print(item)
            save_article_mysql(item)
if __name__ == '__main__':
    main()





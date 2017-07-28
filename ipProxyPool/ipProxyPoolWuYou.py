# -*- coding:UTF-8 -*-
import re

import requests
import json
import redis

mRedis = redis.Redis(host='localhost',port=6379,db=0)

def checkAvaliability(urlWithPort):
    try:
        requests.get('http://sdata.jseea.cn', proxies={"http":urlWithPort},timeout=5)
    except:
        print 'connect failed'
        return False
    else:
        print 'success'
        return True


#checkAvaliability("114.232.116.30:44597")

#针对
def getHtml(urlWithPort):
    http_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'X-Requested-With':'XMLHttpRequest',
        'Host': 'www.data5u.com',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
    }
    mRequests = requests.get('http://www.data5u.com/',headers=http_header)
    pt = re.compile(r'<span><li>([\d\.]+)</li></span>[\w\W]+?port[\w\W]+?>(\d+)')
    resultArray = pt.findall(mRequests.content)
    for item in resultArray:
        concatUrl = item[0]+':'+item[1]
        print concatUrl
        if checkAvaliability(concatUrl):
            # todo 存入redis
            mRedis.rpush("proxyQueue",concatUrl)

getHtml('')
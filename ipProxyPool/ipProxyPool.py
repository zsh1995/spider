# -*- coding:UTF-8 -*-

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
        'Referer': 'http://www.xdaili.cn/freeproxy.html',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With':'XMLHttpRequest',
        'Host': 'www.xdaili.cn',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Cookie':'JSESSIONID=E1ADE0E7BE3581EC709B1FCB2039D242; UM_distinctid=15d743260eafc6-02a918127516ab-8383667-1fa400-15d743260eba55; aliyungf_tc=AQAAAG1ZYSr++AwAemxuJPG66h0weJmV; Hm_lvt_c1c9e8373d7f000ad58265f0b17f1cff=1500893045,1500953782,1500968336,1500968660; Hm_lpvt_c1c9e8373d7f000ad58265f0b17f1cff=1501224849; gdxidpyhxdE=78YbIgfJwGeyPy7Z4jkYzrBvlNOZ1NSidjiXRB%5CHMXg49RTiuMntIUnd0oexTtVXQYLTW1LVcbS9vA75Vfp0psKW%5C6BJ%2BVoNpNBpInZWB0cQpAbq0uVEglGd2%5C6yCMzfR5pCUH%2BnZKnAzoGvd%2FhlRXdZNpqecpy707d%2FVN0k9nj2%2Fwy9%3A1501225795219; _9755xjdesxxd_=31; CNZZDATA1260873131=2090465527-1500892392-null%7C1501221207; _ga=GA1.2.560602440.1500893045; _gid=GA1.2.660564383.1500893045; _gat=1'
    }
    mRequests = requests.get('http://www.xdaili.cn/ipagent/freeip/getFreeIps',params='page=2&rows=10',headers=http_header)
    jsonObject = json.loads(mRequests.content)
    for item in jsonObject['rows']:
        concatUrl = item['ip']+':'+item['port']
        if checkAvaliability(concatUrl):
            # todo 存入redis
            mRedis.rpush("proxyQueue",concatUrl)

getHtml('')
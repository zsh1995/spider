import requests

try:
    requests.get('http://sdata.jseea.cn', proxies={"http":"http://1.199.193.182:31199"},timeout=5)
except:
    print 'connect failed'
else:
    print 'success'
# -*- coding:UTF-8 -*-

import httplib
import threading

from PIL import Image
import pytesseract
import time
import re

def checkCodeIsRight(checkCode,http_header):
    httpClientSub = httplib.HTTPSConnection('query-score.5184.com')
    httpClientSub.request('GET',
                          '/web/captcha/verify?callback=jQuery180043396168267276236_1499738047268&verify_code=' + checkCode + '&_=' + str(
                              int(time.time())), ' ', http_header);
    newResponse = httpClientSub.getresponse();
    newBody = newResponse.read();
    if newBody.find('200'):
        print 'ok!'

    if httpClientSub:
        httpClientSub.close()


for cnt in range(1,2,1):
    pytesseract.pytesseract.tesseract_cmd = 'E:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
    tessdata_dir = '--tessdata-dir "E:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'

    httpClient = None

    http_header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        'Referer':'http://page-resoures.5184.com/cjquery/w/zk/query.html?20170400zk_cj',
        'Accept':'image/webp,image/*,*/*;q=0.8',
    }
    filename = 'checkCode'+str(cnt)+'.jfif'
    outputFile = open(filename,'wb')


    httpClient = httplib.HTTPSConnection('query-score.5184.com')
    httpClient.request('GET','/web/captcha?random=0.9769682579849579',' ',http_header)

    response = httpClient.getresponse();
    print response.getheaders()
    body = response.read()
    outputFile.write(body)
    outputFile.close()
    img = Image.open(filename)
    ##
    imgry = img.convert("L")
    threshold = 120
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    out = imgry.point(table, '1')
    print pytesseract.image_to_string(image=out, lang='eng', config=tessdata_dir)
    #通过验证码验证
    responseHeader = response.getheader('set-cookie')
    responseHeader=str(responseHeader).replace("HttpOnly,","")
    http_header['Cookie']=responseHeader
    checkCode = input('check:')
    print checkCode
    print http_header
    threads = []
    print 'begin ', time.ctime()
    for myCnt in range(10000):
        t1 = threading.Thread(target=checkCodeIsRight, args=(checkCode,http_header))
        threads.append(t1)
    for t in threads:
        t.setDaemon(True)
        t.start()

    t.join()
    print 'end ', time.ctime()

    if httpClient:
        httpClient.close()

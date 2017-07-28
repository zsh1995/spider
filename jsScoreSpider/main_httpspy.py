# -*- coding:UTF-8 -*-
# 720451
import httplib
import urllib
import threadpool
import MySQLdb.cursors
import threading
import socket
import redis


from PIL import Image
import pytesseract
import time
import re



# 工作线程数
ROWS_PER_FETCH = 5

okCnt=0

startData="1758523"

mProxyQueue = "proxyQueue"

mRedis = redis.Redis(host="localhost",port=6379,db=0)


#后期可封装成代理队列类
def getProxy(proxyQueue):
    queueName,proxyUrl = mRedis.blpop(proxyQueue,0)
    fullProxy = proxyUrl.split(':')
    return fullProxy[0],fullProxy[1],proxyUrl

def giveBackProxy(proxyQueue,proxyUrl):
    mRedis.rpush(proxyQueue,proxyUrl)



# 根据身份证和学生姓名查找准考证
def findExamCode(userId, fullName):
    if userId == None or userId == "":
        return
    fullName=fullName.encode('utf8')
    http_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        'Referer': 'http://sdata.jseea.cn/tpl_front/zhuankao/findZkzh.html',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin':'http://sdata.jseea.cn',
        'Host': 'sdata.jseea.cn'
    }
    urlName = urllib.quote(fullName)

    post_data = 'sfzjlx=0&sfzjh={0}&zkzh=&xm={1}'.format(userId, urlName)
    try:
        proxyHost,proxyPort,proxyFull = getProxy(mProxyQueue)
        httpClient = httplib.HTTPConnection(proxyHost,proxyPort,timeout=5)
        print "create httpClient1======================name"+fullName+"===============userId"+str(userId)+"=================currentTime:"+time.ctime()

        httpClient.request('POST', 'http://sdata.jseea.cn/tpl_front/zhuankao/findZkzh.html', post_data, http_header)

        response = httpClient.getresponse();
        # print response.getheaders()
        body = response.read()
        # 归还代理
        # todo 此处应该增加判断是进入网页还是重定向到其他错误页面
        if body.find('公众信息服务平台') <0 :
            raise Exception('此ip被封')
        giveBackProxy(mProxyQueue,proxyFull)
        if body.find(fullName) >= 0:
            pt = re.compile('<td class="tcenter">(?P<examCode>\\d+)</td>\\s+<td class="tcenter">{0}</td>'.format(fullName))
            matchThing = pt.search(body)
            if None != matchThing:
                print matchThing.group('examCode')
                return matchThing.group('examCode')
    except Exception,e:
        print "[RuntimeErro]: ", e
        raise Exception
    finally:
        print "close httpClient1======================name" + fullName + "===============userId" + str(userId) + "=================currentTime:" + time.ctime()
        try:
            httpClient.close()
        except:
            print "close erro"


# 根据准考证号和全名查找成绩
# findExamCode('321321199111013635', '袁成臣')
def getScores(examCode,fullName,certNo):
    global okCnt
    fullName=fullName.encode('utf8')
    print 'will try:'+fullName+',examCode'+examCode
    http_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        'Referer': 'http://sdata.jseea.cn/tpl_front/score/allScoreList.html',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    urlName = urllib.quote(fullName)

    post_data = 'zkzh={0}&ksmx={1}'.format(examCode, urlName)

    try:
        proxyHost,proxyPort,proxyFull = getProxy(mProxyQueue)
        httpClient = httplib.HTTPConnection(proxyHost,proxyPort,timeout=5)
        print "create httpClient2======================name"+fullName+"===============examCode"+examCode+"=================currentTime:"+time.ctime()
        httpClient.request('POST', 'http://sdata.jseea.cn/tpl_front/score/allScoreList.html', post_data, http_header)

        response = httpClient.getresponse();
        #print response.getheaders()

        # 归还代理
        giveBackProxy(mProxyQueue,proxyFull)

        body = response.read()
    except:
        print "http connect erro!!!!!!!httpClient2======================name"+fullName+"===============examCode"+examCode+"=================currentTime:"+time.ctime()
    finally:
        print "close httpClient2======================name" + fullName + "===============examCode" + examCode + "=================currentTime:" + time.ctime()
        try:
            httpClient.close()
        except:
            print "erro close"
    #print body
    # 成绩查询正则表达式
    pt = re.compile('<td class="tcenter">'+examCode+'</td>\\s+<td class="tcenter">(\\d+)</td>\\s+<td class="tcenter">(.+)</td>\\s+<td class="tcenter">(\\d+)</td>\\s+<td class="tcenter">(.+)</td>\\s+<td class="tcenter">(.+)</td>')
    matchResult = pt.findall(body)
    if len(matchResult) <= 0:
        return
    try:
        print "wait to create =============================name"+fullName
        conn = MySQLdb.connect(host='42.62.70.203', user='ent_manager', passwd='CaCl@Ent', db='ent_portal_prod', port=3306,connect_timeout=30,
                           charset='utf8', cursorclass = MySQLdb.cursors.SSCursor)
        print "connnect OK!----------------------name:"+fullName+"----------zkzCode:"+examCode
        mcur=conn.cursor()
        print "get cur OK!----------------------name:"+fullName+"----------zkzCode:"+examCode
        for cnt in range(0,len(matchResult)):
            examDate = matchResult[cnt][3]
            getDate = re.compile(r'(\d+)')
            getDateResult = getDate.findall(examDate)
            examDate='{0}-{1}-{2}'.format(getDateResult[0],getDateResult[1],getDateResult[2])
            examinfo = "(code:{0},name:{1},score:{2},data:{3})".format(matchResult[cnt][0],matchResult[cnt][1],matchResult[cnt][2],examDate)
            okCnt = okCnt+1

            print 'okCnt:'+okCnt
            #sql ="INSERT INTO js_zk_score( student_name, zkzCode, cert_no, score_info) VALUE ( '{0}', '{1}', '{2}', '{3}' ) ON DUPLICATE KEY UPDATE score_info = CONCAT(score_info, ';', '{3}')".format(fullName,examCode,certNo,examinfo)
            #mcur.execute(sql)
            #conn.commit()
        print "commit ok ----------------------name:"+fullName+"----------zkzCode:"+examCode
    except:
        print('This is a \033[1;35m erro \033[0m! examCode='+examCode)
        raise Exception
    finally:
        mcur.close()
        conn.close()
        print "close OK!----------------------name:"+fullName+"----------zkzCode:"+examCode



def threadWorker(arrayList):
    if(len(arrayList)==0):
        return
    elem = arrayList.pop()
    try:
        dataScrap(elem[0][0],elem[0][1],elem[0][2],elem[0][3])
    except Exception,e:
        # 错误重试
        arrayList.append(elem)
    time.sleep(0.5)



def dataScrap(id,fullname,cid1,cid2):
    examCode = findExamCode(cid1,fullName=fullname)
    if examCode is not None:
        getScores(examCode,fullname,cid1)
        return
    examCode = findExamCode(cid2,fullname)
    if examCode is not None:
        getScores(examCode,fullname,cid2)
        return


def arrayModify(arrayInput):
    if arrayInput is None:
        return None
    changeA = []
    for item in arrayInput:
        mList=[]
        for iitem in item:
            mList.append(iitem)
        changeA.append((mList,None))
    return changeA




if __name__ == '__main__':
    # 主流程

    # 从数据库取一组

    # 根据数据进行采集，采集结果写入数据库
    # 采用线程池
    #

    conn = MySQLdb.connect(host='42.62.70.203', user='ent_manager', passwd='CaCl@Ent', db='ent_portal_prod', port=3306,
                       charset='utf8', cursorclass = MySQLdb.cursors.SSCursor)
    sql = "SELECT a.stu_id AS id, tui.username AS fullName, tui.cert_no AS cid1, '' AS cid2 FROM ent_order a INNER JOIN sch_org_school b ON b.id = a.school_id INNER JOIN sch_local_province c ON c.id = b.province_id LEFT JOIN t_user_info tui ON tui.id = a.stu_id WHERE a.channel_code = 'OC_SCHOOL' AND c.id = 16  GROUP BY a.stu_id UNION SELECT c.stu_id AS id, tui.username AS fullName, tui.cert_no AS cid1, '' AS cid2 FROM ent_ord_details a INNER JOIN ent_ord_enroll b ON b.ord_detail_id = a.id INNER JOIN ent_order c ON c.id = a.ord_id LEFT JOIN t_user_info tui ON tui.id = c.stu_id WHERE b.province_id = 16  GROUP BY c.stu_id"
    cur = conn.cursor();
    cur.execute(sql)

    pool = threadpool.ThreadPool(ROWS_PER_FETCH)


    getArray = cur.fetchmany(ROWS_PER_FETCH)
    getArray = arrayModify(getArray)

    while True:
        if(len(pool.workRequests) < 10):
            requests = threadpool.makeRequests(threadWorker, [getArray,])
            [pool.putRequest(req) for req in requests]
        pool.poll(False)
        if(len(getArray) == 0):
            newArray = cur.fetchmany(ROWS_PER_FETCH)
            if newArray is None:
                break;
            getArray.extend(arrayModify(newArray))
            try:
                print 'one circle:' + str(getArray[-1][0][0])
            except Exception, e:
                print e
            time.sleep(1)
    pool.wait()
    cur.close()
    conn.close()

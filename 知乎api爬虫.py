import requests
import bs4
import pickle
import re
import os.path
'''免登录版本
    通过authorization获得授权
    该authorization是知乎对于google等搜索引擎的授权'''



def getQid(headers, url=r'https://www.zhihu.com/topic/19552832/top-answers'):
    '''从话题页面获取所有问题的id,形成生成器'''
    response = requests.get(url=url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    urlList = soup.find_all(name='link', itemprop='url')
    # 获取页数
    n = soup.find_all(href=re.compile('page='))[-2].string
    n = int(n)
    for count in range(1, n+1):
        response = requests.get(url=url, headers=headers, params={'page': count})
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        urlList = soup.find_all(name='link', itemprop='url')
        i = 0
        for x in urlList:
            i += 1
            if i % 2 == 0:
                yield str(x['href']).split('/')[-3]


def getAnswers(Qid, headers, url=r'https://www.zhihu.com/api/v4/questions/'):
    '''将Qid对应的所有answer数据存储于一个列表中,return answers list'''
    print(Qid)  # 输出question id
    list = []
    #用params控制返回的json数据中data部分的内容
    #content是带格式的answer内容
    params = {#所有信息都有
        'include':'data[*].\
        is_normal,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,\
        content,\
        editable_content,voteup_count,reshipment_settings,comment_permission,\
        mark_infos,created_time,updated_time,relationship.is_authorized,is_author,\
        voting,is_thanked,is_nothelp,upvoted_followees;\
        data[*].author.badge[?(type=best_answerer)].topics',
        'limit':'20',
        'offset':'0'
    }
    params2 = {#简要信息
        'include':'data[*].content, \
        data[*].author.badge[?(type=best_answerer)].topics',
        'limit':'20',
        'offset':'0'
    }
    response = requests.get(url+Qid+'/answers', headers=headers, params=params2)
    list.append(response.json())
    print(response.url)
    while response.json()['paging']['is_end'] is False:
        url = response.json()['paging']['next'].replace('http', 'https')
        response = requests.get(url=url, headers=headers)
        list.append(response.json())
        print(url)
    return list


def save(Qid, list, dir='d://topic python/'):
    '''将qa字典保存到文件中，格式化保存or文本保存'''
    f = open(dir+Qid, 'wb')
    pickle.dump(list, f)
    f.close()
    print('save file :{}'.format(dir+Qid))


def spider():
    cookie = 'd_c0="ABACzN_uTguPTryqTQ-ZJKjmJHaxJMGH0Us=|1487055671"; \
        _zap=a95ba3e3-d4af-44d0-98e8-ae3e3d07b987; _xsrf=90aa5b8eafd9c3185b3ea0e1b8ecd797; \
        q_c1=832f6b72e65f41bcac72abeb3eb63e25|1492739085000|1487055672000; \
        __utma=51854390.550964018.1487055670.1492784076.1492784214.10; \
        __utmb=51854390.0.10.1492784214; __utmc=51854390; \
        __utmz=51854390.1492784214.10.10.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); \
        __utmv=51854390.000--|2=registration_date=20140306=1^3=entry_date=20170214=1; l_n_c=1; \
        r_cap_id="NDQ2NzU5NmNiM2Q1NDVjNmJkNTlhZTdlOWVkOGMxMTM=|1492785357|97562ed5d19ea88a846b6dcaf97b12fbb766f4df"; \
        cap_id="MWMxZjY4MzlmZWEwNDhiNTk5NWM2MGRiN2E4OGYxMjI=|1492785357|bbc26290d045711ccb0369a2cdf24c468f0620ee"; \
        l_cap_id="MmJhYzFmY2RkZjgzNGQxYWEwNmFkY2YwNDFhZmQyMjA=|1492785357|0532472a56053becc7377634b42d6f6c615be61d"; n_c=1'
    headers = {
        #'Cookie': cookie,
        #'x-udid': 'ABACzN_uTguPTryqTQ-ZJKjmJHaxJMGH0Us=',
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
        'User-Agent': 'Baiduspider'
    }
    i = 0
    # 存储抓取过的问题的id
    QidList = []
    for x in getQid(headers=headers):
        # 判断该问题是否已经抓取
        if x not in QidList:
            i = i + 1
            print(i, end=' : ')
            QidList.append(x)
            list = getAnswers(Qid=x, headers=headers)
            save(x, list)


def getFileList(dir='E://学习文件/爬虫获取到的数据/topic-python-zhihu/'):
    for f in os.listdir(dir):
        if os.path.isfile(os.path.join(dir,f)):
            yield (dir+f)


def read(fileFullPath):
    f = open(fileFullPath, 'rb')
    data = pickle.load(f)
    print(fileFullPath.split('/')[-1],end=' : ')
    print(len(data))
    for x in data:
        print(x)


def main():
    #spider()
    #for fileFullPath in getFileList(dir='d://topic python/'):
    #    read(fileFullPath)


if __name__ == '__main__':
    main()

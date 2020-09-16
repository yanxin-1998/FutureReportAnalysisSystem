import requests
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIDERNAME='金投网'

def parseJinTouTimeStr(timeString):
    #'11-13 08:19'
    time_string=datetime.now().strftime('%Y-')+timeString.strip()
    struct_time = datetime.strptime(time_string, '%Y-%m-%d %H:%M')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseCnGolgContent(url):
    r=sess.get(url)
    selector=etree.HTML(r.text)
    #两种页面结构
    temp_ls=selector.xpath("//div[@id='zoom'] | //div[@class='article_con']")
    if temp_ls:
        ele=temp_ls[0]
        content=ele.xpath("string(.)").strip()
    else:
        print('抓取不到正文内容',url)
        content=''
    # print(content)
    return content


def getJinTouArticleLs(articleCol,BeCrawledUrlList):
    url='https://futures.cngold.org/zhzx/'

    temp_article_ls=[]
    for url in (url,):
        r=sess.get(url)
        r.encoding='utf-8'   
        selector=etree.HTML(r.text)
        #列表里的每一个item
        eleList=selector.cssselect(".list_article ul li")
        for ele in eleList:
            articleUrl=ele.xpath("./div[@class='tit']/a/@href")[0]
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath("./div[@class='tit']/a/text()")[0]
            #btm clearfix
            publicTime=parseJinTouTimeStr(ele.xpath("./div[@class='btm clearfix']/span[@class='pubtime']/text()")[0])
            temp_dict={'tags':['cngold'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='cngold'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
             #文章内容
            content=parseCnGolgContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            if n:
                print(SPIDERNAME,'   ',title,"  ",n)
                temp_dict['product_name']=n
                #品种映射板块
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                temp_dict['product_name']=''
                temp_dict['group']=''
            temp_article_ls.append(temp_dict)

     #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,'金投网')


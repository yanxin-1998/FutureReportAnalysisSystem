import requests
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIDERNAME='金融界'
def parseJinrongjiePubTime(string):
    #时间：2019-10-18
    string=string.strip()+' 00:00:00'
    
    return string

def parseJinrongjieContent(url):
    r=sess.get(url)
    r.encoding='gbk' 
    selector=etree.HTML(r.text)
    ele=selector.cssselect("div.texttit_m1")[0]
    content=ele.xpath("string(.)").strip()
    # print(content)
    return content

def getJinrongjieArticleList(articleCol,BeCrawledUrlList):
    #金属
    url1='http://futures.jrj.com.cn/list/jszx.shtml'
    #能源化工
    url2='http://futures.jrj.com.cn/list/nyhgzx.shtml'
    #农产品
    url3='http://futures.jrj.com.cn/list/ncpzx.shtml'


    temp_article_ls=[]

    for url in (url1,url2,url3):
        r=sess.get(url)
        r.encoding='gbk'    #不做任何设置的时候，正确
        selector=etree.HTML(r.text)
        eleList=selector.xpath("//ul[@class='jrj-l1 tab-ts jrj-f14']/li")
        for ele in  eleList:
            try:
                articleUrl=ele.xpath('./label/a/@href')[0]
            except IndexError as e:
                print('跳过空行')
                continue
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./label/a/@title')[0]
            publicTime=parseJinrongjiePubTime(ele.xpath('./label/i/text()')[0])
            temp_dict={'tags':['Jinrongjie'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='Jinrongjie'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
             #文章内容
            content=parseJinrongjieContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            if n:
                print(SPIDERNAME,'   ',title,"  ",n)
                temp_dict['product_name']=n
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                temp_dict['product_name']=''
                temp_dict['group']=''
            
            temp_article_ls.append(temp_dict)
    
     #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,SPIDERNAME)
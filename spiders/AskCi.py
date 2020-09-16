from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
import requests
SPIDERNAME='中商情报网'
def parseAskCiPubTime(string):
    #时间：2019-10-18 07:53:36
    
    struct_time = datetime.strptime(string, '时间：%Y-%m-%d %H:%M:%S')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseAskCiContent(url):
    r=sess.get(url)
    r.encoding='utf8'
    selector=etree.HTML(r.text)
    ele=selector.cssselect(".detail_content_text")[0]
    content=ele.xpath("string(.)").strip()
    # print(content)
    return content

def getAskCiArticleList(articleCol,BeCrawledUrlList):
    Url='http://www.askci.com/news/chanye/'

    temp_article_ls=[]

    for url in (Url,):
        r=sess.get(url)
        r.encoding='utf8'    #不做任何设置的时候，正确
        selector=etree.HTML(r.text)
        eleList=selector.cssselect(".list_box1 ul li")
        for ele in  eleList:
            try:
                articleUrl=ele.xpath('./a/@href')[0]
            except:
                continue
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./a/@title')[0]
            publicTime=ele.xpath('./div/div/div[@class="list_box1_time"]/text()')[0]
            temp_dict={'tags':['AskCi'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='AskCi'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
             #文章内容
            content=parseAskCiContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            if n:
                print(SPIDERNAME,'   ',title,"  ",n)
                temp_dict['product_name']=n
                temp_dict['group']=ProductToGroup[n]
                #找根据文章内容找不到品种的文章，跳过
                temp_article_ls.append(temp_dict)
            else:
                print("………………………………未找到品种名称，可能异常")

            
            
    
     #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,SPIDERNAME)
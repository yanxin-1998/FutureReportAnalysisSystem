import requests
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIDERNAME='东方财富期货'
def parseEastMoneyPubTime(time_string):
    #s='10月18日 14:08'
    time_string=datetime.now().strftime('%Y-')+time_string.strip()
    struct_time = datetime.strptime(time_string, '%Y-%m月%d日 %H:%M')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseEastMoneyContent(url):
    r=sess.get(url)
    selector=etree.HTML(r.text)
    ele=selector.xpath("//div[@id='ContentBody']")[0]
    content=ele.xpath("string(.)").strip().strip('\n')
    # print(content)
    return content


def getEastMoneyArticleList(articleCol,BeCrawledUrlList):
    url_1='http://futures.eastmoney.com/a/cqhdd.html'  #期货导读
    url_2='http://futures.eastmoney.com/news/cjdgc.html'  #焦点观察
    url_3='http://futures.eastmoney.com/news/cqspl.html'  #内盘评论
    url_4='http://futures.eastmoney.com/news/cwpsd.html'  #外盘速递
    url_5='http://futures.eastmoney.com/news/cqsyw.html'  #期市聚焦
    
    temp_article_ls=[]

    for url in (url_1,url_2,url_3,url_4,url_5):
        r=sess.get(url)
        # r.encoding='gb2313'   
        selector=etree.HTML(r.text)
        eleList=selector.xpath("//ul[@id='newsListContent']/li/div[@class='text']")
        for ele in  eleList:
            articleUrl=ele.xpath("./p[@class='title']/a/@href")[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath("./p[@class='title']/a/text()")[0].strip()
            publicTime=parseEastMoneyPubTime(ele.xpath("./p[@class='time']/text()")[0])
            temp_dict={'tags':['eastmoney'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='eastmoney'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
             #文章内容
            content=parseEastMoneyContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            if n:
                print(SPIDERNAME,'   ',title,'     ',n)
                temp_dict['product_name']=n
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                temp_dict['product_name']=''
                temp_dict['group']=''
            temp_article_ls.append(temp_dict)
    
     #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,'东方财富')
    
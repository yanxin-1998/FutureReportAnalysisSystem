import requests,os,time
from datetime import datetime,timedelta
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIDERNAME='上海有色'
def parseSMMArtPubTime(time_string):
    #9分钟前    3小时前
    time_string=time_string.strip()
    if '分钟' in time_string:
        m=int(time_string.strip('分钟前'))
        delta=timedelta(minutes=m)
    elif '小时' in time_string:
        m=int(time_string.strip('小时前'))
        delta=timedelta(hours=m)
    else:#2019-12-23
        time_string+' 00:00:00'
        return time_string+' 00:00:00'

    time_obj=datetime.now()-delta
    return time_obj.strftime('%Y-%m-%d %H:%M:%S')

def parseSMMArtContent(url):
    r=sess.get(url)
    r.encoding='utf8'
    selector=etree.HTML(r.text)
    ele_ls=selector.cssselect(".news-detail-article-content")
    if ele_ls:
        ele=ele_ls[0]
        content=ele.xpath("string(.)").strip()
    else:
        print('页面内容为空',url)
        content=''
    # print(content)
    return content

def getSMMArticleList(articleCol,BeCrawledUrlList):
    #要闻
    url1='https://news.smm.cn'

    #[{'title':'      ','url':'      ','publicTime':'      ','tags':[],'score':0},]
    #历史爬取的记录

    temp_article_ls=[]
    
    for url in (url1,):
        r=sess.get(url)
        r.encoding='utf8'
        selector=etree.HTML(r.text)
        eleList=selector.cssselect(".news-main-list>ul>li")
        for ele in  eleList:
            articleUrl='https://news.smm.cn'+ele.xpath('./div/a/@href')[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./div/a/h3/@title')[0]
            # print(title)
            # continue
            publicTime=parseSMMArtPubTime(ele.xpath('./div/div[@class="news-list-content-label"]/p/label[@class="news-list-time-label"]/text()')[0])
            temp_dict={'tags':['SMM'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='SMM'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseSMMArtContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            if n:
                print(SPIDERNAME,'   ',title,"    ",n,'   ',publicTime)
                temp_dict['product_name']=n
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                temp_dict['product_name']=''
                temp_dict['group']=''

            temp_article_ls.append(temp_dict)

    #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,SPIDERNAME)
    
   


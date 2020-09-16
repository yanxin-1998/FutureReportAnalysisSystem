import requests,json,os,time
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIERNAME='天然橡胶网'##天然橡胶网
def parseYunkenArtPubTime(time_str):
    #2019-10-13T08:30:59+08:00
    struct_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+08:00')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseYunkenArtContent(url):
    r=sess.get(url)
    selector=etree.HTML(r.text)
    #//div[@id='whitewrap']/div[2]/div/section/section[2]/div[3]/div/div/article/div
    ele=selector.xpath("//div[@id='whitewrap']/div[2]/div/section/section[2]/div[3]/div/div/article/div")[0]
    content=ele.xpath("string(.)").strip().strip('\n')
    # print(content)
    return content

def getYunkenArticleList(articleCol,BeCrawledUrlList):
    yunkenUrl='https://www.yunken.com/?cat=7'
    

    temp_article_ls=[]
    for url in (yunkenUrl,):
        r=sess.get(url)
        r.encoding='utf8'
        selector=etree.HTML(r.text)
        eleList=selector.xpath("//section[2]//article/header")
        for ele in  eleList:
            articleUrl=ele.xpath('./h3/a/@href')[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./h3/a/text()')[0]
            publicTime=parseYunkenArtPubTime(ele.xpath('./div/time/@datetime')[0])   
            temp_dict={'tags':['天然橡胶网','橡胶'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='yunken'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseYunkenArtContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            if n:
                print(SPIERNAME,'   ',title,'     ',n)
                temp_dict['product_name']=n
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                temp_dict['product_name']=''
                temp_dict['group']=''

            temp_article_ls.append(temp_dict)
    #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,'天然橡胶网')
   
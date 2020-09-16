import requests
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIERNAME='中国粮油信息网'
def parseChinaGrainPubTime(string):
    #时间：2019-10-18 07:53:36
    
    struct_time = datetime.strptime(string, '时间：%Y-%m-%d %H:%M:%S')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseChinaGrainContent(url):
    r=sess.get(url)
    selector=etree.HTML(r.text)
    ele=selector.xpath("//div[@class='article-conte-infor']")[0]
    content=ele.xpath("string(.)").strip().replace('\n','')
    # print(content)
    return content

def getChinaGrainArticleList(articleCol,BeCrawledUrlList):
    Url='http://www.chinagrain.cn/analytics/'

    temp_article_ls=[]

    for url in (Url,):
        r=sess.get(url)
        # r.encoding='gb2313'    #不做任何设置的时候，正确
        selector=etree.HTML(r.text)
        eleList=selector.xpath("//ul[@id='list']/li")
        for ele in  eleList:
            articleUrl=ele.xpath('./a/@href')[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./a/h2/text()')[0]
            publicTime=parseChinaGrainPubTime(ele.xpath('./span[2]/text()')[0])
            temp_dict={'tags':['chinagrain'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='chinagrain'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
             #文章内容
            content=parseChinaGrainContent(articleUrl)
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
    HandleTmpList(temp_article_ls,articleCol,'中国粮油信息网')
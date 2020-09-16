import requests
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIDERNAME='我的农产品'
def parseMyagricArtPubTime(string):
    #2019-10-12 17:25   
    return string

def parseAgricArtContent(url):
    r=sess.get(url)
    r.encoding='gb2312'
    selector=etree.HTML(r.text)
    try:
        ele=selector.xpath("//div[@id='text']")[0]
        content=ele.xpath("string(.)").strip().strip('\n')
    except IndexError as e:
        print('网页内容为空',url)
        content=''
    # print(content)
    return content

def getMyagricArticle(articleCol,BeCrawledUrlList):
    dadou='https://www.myagric.com/article/p-4093----070201---------1.html'
    doupo='https://www.myagric.com/article/p-4093----070301,070202---------1.html'
    youzhi='https://www.myagric.com/article/p-4093----0701---------1.html'
    temp_article_ls=[]
    for url in dadou,doupo,youzhi:
        r=sess.get(url)
        r.encoding='gb2312'
        selector=etree.HTML(r.text)
        eleList=selector.xpath("//ul[@id='list']/li[not(@class)]")
        for ele in  eleList:
            articleUrl='https:'+ele.xpath('./a/@href')[0]
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./a/text()')[0]

            publicTime=parseMyagricArtPubTime(ele.xpath('./span/text()')[0])
   

            temp_dict={'tags':['myagric'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='myagric'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()

            #文章内容
            content=parseAgricArtContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)

            if n:
                temp_dict['product_name']=n
                print(SPIDERNAME,'   ',title,'     ',n)
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                
                temp_dict['product_name']=''
                temp_dict['group']=''
            
            temp_article_ls.append(temp_dict)

     #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,SPIDERNAME)
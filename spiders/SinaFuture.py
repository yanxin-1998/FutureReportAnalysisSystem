import requests,json,os,time
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIERNAME='新浪期货'
def parseSinaArtPubTime(time_string):
    #s='(10月12日 09:18)'
    time_string=datetime.now().strftime('%Y')+time_string
    struct_time = datetime.strptime(time_string, '%Y(%m月%d日 %H:%M)')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')
    
def parseSinaArtContent(url):
    r=sess.get(url)
    r.encoding='utf8'
    selector=etree.HTML(r.text)
    ele_ls=selector.xpath("//div[@id='artibody']")
    if ele_ls:
        ele=ele_ls[0]
        content=ele.xpath("string(.)").strip()
    else:
        print('页面内容为空',url)
        content=''
    # print(content)
    return content

def getSinaArticleList(articleCol,BeCrawledUrlList):
    sinaFarmingProductUrl='http://finance.sina.com.cn/roll/index.d.html?lid=1006'
    sinaIndustryProductUrl='http://finance.sina.com.cn/roll/index.d.html?lid=1005'
    sinaEnergyProductUrl='http://finance.sina.com.cn/roll/index.d.html?lid=1007'

    #[{'title':'      ','url':'      ','publicTime':'      ','tags':[],'score':0},]
    #历史爬取的记录

    temp_article_ls=[]
    for url in (sinaEnergyProductUrl,sinaFarmingProductUrl,sinaIndustryProductUrl):
        r=sess.get(url)
        r.encoding='utf8'
        selector=etree.HTML(r.text)
        #定位每一篇文章
        eleList=selector.xpath("//ul[@class='list_009']/li")
        for ele in  eleList:
            #链接
            articleUrl=ele.xpath('./a/@href')[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./a/text()')[0]
            publicTime=parseSinaArtPubTime(ele.xpath('./span/text()')[0])
            temp_dict={'tags':['sina'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='sina'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseSinaArtContent(articleUrl)
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
    HandleTmpList(temp_article_ls,articleCol,SPIERNAME)
    
   


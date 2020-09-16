import requests,time,re,json
from lxml import etree
from datetime import datetime
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIDERNAME='和讯财经'
def parseHexunArtPubTime(time_string):
    #'11/13 08:19'
    time_string=datetime.now().strftime('%Y-')+time_string.strip()
    struct_time = datetime.strptime(time_string, '%Y-%m/%d %H:%M')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseHexunContent(url):
    r=sess.get(url)
    r.encoding='gbk'
    selector=etree.HTML(r.text)
    try:
        ele=selector.cssselect("div.art_contextBox")[0]
        content=ele.xpath("string(.)").strip().strip('\n')
    except:
        print('有错误     ',url)
        content=''
    
    # print(content)
    return content

def getHexunArticleList(articleCol,BeCrawledUrlList):
    #农副
    hexunFarmingReqID='101065616'
    #有色
    hexunMetalReqID='101065619'  
    #能源
    hexunEnergyReqID='130519488'
    #化工
    hexunChemicalReqID='130518597'

    temp_article_ls=[]
    header={
            'Referer':'http://futures.hexun.com/agriculturenews/',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
    url='http://open.tool.hexun.com/MongodbNewsService/newsListPageByJson.jsp'
    for ID in (hexunFarmingReqID,hexunMetalReqID,hexunEnergyReqID,hexunChemicalReqID):
        param={
        'id':ID,
        's':'30',
        'cp':'1',
        'priority':'0',
        'callback':'hx_json1%d'%(int(time.time()*1000))
        }
        r=sess.get(url,params=param,headers=header)
        r.encoding='gb2312'    #不做任何设置的时候，正确
        # print(r.text)
        # break
        # selecattor=etree.HTML(r.text)
        # eleList=selector.cssselect("div#temp01 ul li")
        # print('123',eleList)
        article_ls=json.loads(re.search('{.+}',r.text).group())['result']
        for item in  article_ls:
            articleUrl=item['entityurl']
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=item['title']
            publicTime=parseHexunArtPubTime(item['entitytime'])
            temp_dict={'tags':['hexun'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='hexun'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseHexunContent(articleUrl)
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
            # print(temp_dict)
            temp_article_ls.append(temp_dict)

    #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,'和讯财经')
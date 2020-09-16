import requests
from lxml import etree
from datetime import datetime
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess

SPIDERNAME='我的钢铁网'
def parseMysteelArtPubTime(string):
    #2019-10-12 17:25   
    return string

def parseMystellArtContent(url):
    r=sess.get(url)
    selector=etree.HTML(r.text)
    try:
        ele=selector.xpath("//div[@id='text']")[0]
        content=ele.xpath("string(.)").strip().strip('\n')
    except IndexError as e:
        print('网页内容为空',url)
        content=''
    # print(content)
    return content

def getMysteelArticleList(articleCol,BeCrawledUrlList):
    mysteelFarmingUrl='https://news.mysteel.com/article/p-3816-------------1.html'
    #有色
    mysteelNonferrousUrl='https://news.mysteel.com/article/p-2480-------------1.html'  
    mysteelBlackmetalUrl='https://news.mysteel.com/article/p-3822-------------1.html'
    #能源化工
    EnergyAndChemical='https://news.mysteel.com/article/p-3823-------------1.html'



    temp_article_ls=[]
    for url in (mysteelBlackmetalUrl,mysteelFarmingUrl,mysteelNonferrousUrl,EnergyAndChemical):
        r=sess.get(url)
        # r.encoding='gb2313'    #不做任何设置的时候，正确
        selector=etree.HTML(r.text)
        eleList=selector.xpath("//ul[@id='news']/li")
        for ele in  eleList:
            articleUrl='https:'+ele.xpath('./h3/a/@href')[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./h3/a/text()')[0]
            try:
                publicTime=parseMysteelArtPubTime(ele.xpath('./p/text()')[0])
            except:
                print(url,'   ',title,'   找不到时间字符串')
            temp_dict={'tags':['mysteel'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='mysteel'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseMystellArtContent(articleUrl)
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
    # print('mysteel: %d  条'%articleCol.count_documents({'from':'mysteel'}))
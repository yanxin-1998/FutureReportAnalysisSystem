import requests,time
from lxml import etree
from datetime import datetime
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIDERNAME='期货日报'
def parseQHRBArtPubTime(string):
    #5月8日 9:37

    time_string=datetime.now().strftime('%Y-')+string.strip()
    struct_time = datetime.strptime(time_string, '%Y-%m月%d日 %H:%M')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseQHRBArtContent(url):
    r=sess.get(url)
    r.encoding='utf8'
    selector=etree.HTML(r.text)
    try:
        ele=selector.cssselect("div.article-content")[0]
        content=ele.xpath("string(.)").strip().strip('\n')
    except IndexError as e:
        print('网页内容为空',url)
        content=''
    # print(content)
    return content

def getQHRBArticleList(articleCol,BeCrawledUrlList):
    print(SPIDERNAME)
    #农产品
    url1='http://www.qhrb.com.cn/farm/'
    #金属
    url2='http://www.qhrb.com.cn/metal/'  
    #能源化工
    url3='http://www.qhrb.com.cn/energy/'
    #实市场告
    url4='http://www.qhrb.com.cn/comment/scbg/'



    
    for url in (url1,url2,url3,url4):
        r=sess.get(url)
        r.encoding='utf8'    #不做任何设置的时候，正确
        selector=etree.HTML(r.text)
        #之前好几年的内容放在一页，只取5*12条
        eleList=selector.cssselect(".list-point li.item")[:600]
        temp_article_ls=[]
        for ele in  eleList:
            # time.sleep(0.5)
            articleUrl=ele.xpath("./a/@href")[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:break
            title=ele.xpath('./a/text()')[0]
            try:
                publicTime=parseQHRBArtPubTime(ele.xpath('./span/text()')[0])
            except:
                print(url,'   ',title,'   找不到时间字符串')

            temp_dict={'tags':['期货日报'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='期货日报'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseQHRBArtContent(articleUrl)
            temp_dict['content']=content
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            
            if n:
                temp_dict['product_name']=n
                print(SPIDERNAME,'   ',title,"    ",n)
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                
                temp_dict['product_name']=''
                temp_dict['group']=''
            
            temp_article_ls.append(temp_dict)

        #注意缩进不要错
        HandleTmpList(temp_article_ls,articleCol,SPIDERNAME)
        # print('mysteel: %d  条'%articleCol.count_documents({'from':'mysteel'}))
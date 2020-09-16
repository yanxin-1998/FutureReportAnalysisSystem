import requests,json,os,time,re
from datetime import datetime
from lxml import etree
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,sess
SPIERNAME='同花顺'

def parseTongHuaArtPubTime(timeString):
    #03月20日 12:13
    time_string=datetime.now().strftime('%Y-')+timeString.strip()
    struct_time = datetime.strptime(time_string, '%Y-%m月%d日 %H:%M')
    return struct_time.strftime('%Y-%m-%d %H:%M:%S')

def parseTongHuaArtContent(url):
    #mp.weixin.qq.com
    r=sess.get(url)
    r.encoding='gbk'
    selector=etree.HTML(r.text)
    try:
        ele=selector.cssselect('.atc-content')[0]  #有隐患，
        content=ele.xpath('string(.)').strip()
    except:
        print(url)
        if 'mp.weixin.qq.com' in r.text:
            WX_url=re.search('URL=(.+?)\"',r.text).group(1)
            r=sess.get(WX_url)
            selector=etree.HTML(r.text)
            content=selector.xpath("//div[@id='js_content']")[0].xpath('string(.)')
            # print('微信++++++++++++',content)
        else:
            content=''
        
    return content

def getTongHuaArtList(articleCol,BeCrawledUrlList):
    youse='http://goodsfu.10jqka.com.cn/ptjszx_list/'
    nongchanp='http://goodsfu.10jqka.com.cn/ncpzx_list/'
    huagong='http://goodsfu.10jqka.com.cn/nyhgzx_list/'

    total_article_ls=[]
    for url in (youse,nongchanp,huagong):
        r=sess.get(url)
        r.encoding='gbk'
        selector=etree.HTML(r.text)
        eleList=selector.cssselect(".list-con ul li")
        for ele in  eleList:
            articleUrl=ele.xpath('./span/a/@href')[0]
            #判断是否已经爬取过，如果是，跳出循环
            if articleUrl in BeCrawledUrlList:continue
            title=ele.xpath('./span/a/text()')[0]
            publicTime=parseTongHuaArtPubTime(ele.xpath('./span/span/text()')[0])
            temp_dict={'tags':['同花顺'],'score':0,'uid':UID()}
            temp_dict['title']=title.strip()
            temp_dict['articleFrom']='同花顺'
            temp_dict['url']=articleUrl.strip()
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseTongHuaArtContent(articleUrl)
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


            total_article_ls.append(temp_dict)

    #注意缩进不要错
    HandleTmpList(total_article_ls,articleCol,'同花顺')

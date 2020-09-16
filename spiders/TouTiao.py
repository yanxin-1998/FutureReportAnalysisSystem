import requests,time,re
from lxml import etree
from datetime import datetime
from urllib import parse
from common import UID,HandleTmpList,parseContentToName,ProductToGroup,ProductNameTuple
SPIDERNAME='JinRiTouTiao'
def parseTouTiaoArtPubTime(timeStr):
    #"1576477508"
    time_local = time.localtime(float(timeStr))#格式化时间戳为本地时间
    time_YmdHMS = time.strftime("%Y-%m-%d %H:%M:%S",time_local)#自定义时间格式
    return time_YmdHMS

def parseTouTiaoArtContent(url,sess):
    r=sess.get(url)
    r.encoding='utf8'
    try:
        text=re.findall(r"content: '(.+)'",r.text)[0]

    except IndexError as e:
        print('正则匹配错误   ',url)
        return ''
    text=re.sub(r'\\u003C.+?\\u003E','',text)
    text=re.sub(r'&quot','',text)
    return text

def getTouTiaoArticleLs(articleCol,BeCrawledUrlList):
    sess=requests.session()
    searchUrl='https://www.toutiao.com/api/search/content/'
    temp_article_ls=[]
    for productName in ProductNameTuple:
        param={
        'aid': '24',
        'app_name': 'web_search',
        'offset': '20',
        'format': 'json',
        'keyword': productName,
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis', 
        'timestamp':str(int(time.time()*1000))
        }
        sess.headers={
            'cookie': 'tt_webid=6767227851205821960; WEATHER_CITY={}; tt_webid=6767227851205821960; csrftoken=a36cb44b8e05ea4ad645dff6911d86cd; s_v_web_id=7e37f07e972f8c6f1b40a031bb6da223; __tasessionId=vyaf0l09q{}'.format(parse.quote('武汉'),str(int(time.time()*1000))),
            'referer': 'https://www.toutiao.com/search/?keyword={}'.format(parse.quote(productName)),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }
        r=sess.get(searchUrl,params=param)
        temp_ls=r.json()['data']
        for item in temp_ls:
            try:
                articleUrl='https://www.toutiao.com/a%s/'%item['item_id']
            except KeyError as e:
                print(e)
                print('取不到字段,可能有错，跳过')
                continue

            if articleUrl in BeCrawledUrlList:continue
            temp_dict={'tags':['toutiao'],'score':0,'uid':UID()}
            title=item['title']
            temp_dict['articleFrom']='toutiao'
            temp_dict['url']=articleUrl.strip()
            publicTime=parseTouTiaoArtPubTime(item['publish_time'])
            temp_dict['publicTime']=publicTime.strip()
            #文章内容
            content=parseTouTiaoArtContent(articleUrl,sess)
            #定文章所属期货品种,板块
            n=parseContentToName(title+content)
            if n:
                print(SPIDERNAME,'   ',title,"    ",n)
                temp_dict['product_name']=n
                temp_dict['group']=ProductToGroup[n]
            else:
                print("………………………………未找到品种名称，可能异常")
                temp_dict['product_name']=''
                temp_dict['group']=''

            temp_article_ls.append(temp_dict)
            
        
    #注意缩进不要错
    HandleTmpList(temp_article_ls,articleCol,'今日头条')



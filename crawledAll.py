#引入所有网站的爬虫文件
from spiders import Myagric,TongHua,SinaFuture,Mysteel,TouTiao,Yunken,ChinaGrain,EastMoney,Hexun,CnGold,QHRB,Jinrongjie,AskCi,SMM
import pymongo,os
from threading import Thread
from time import sleep
#表对象
# articleCol= pymongo.MongoClient().FutureArticleDB.articleCollection
articleCol= pymongo.MongoClient('127.0.0.1',27017)['python58']['article']
#已经爬取的链接列表
BeCrawledUrlList=[]
for item in articleCol.find({},{'url':1}):       #第一个{}放where条件，第二个{} 指定那些列显示和不显示 （0表示不显示 1表示显示)
    BeCrawledUrlList.append(item.get('url',''))


#每一个网站的爬虫的入口函数
FuncList=[
    Myagric.getMyagricArticle,
    SinaFuture.getSinaArticleList,
    Mysteel.getMysteelArticleList,
    Yunken.getYunkenArticleList,
    ChinaGrain.getChinaGrainArticleList,
    EastMoney.getEastMoneyArticleList,
    Hexun.getHexunArticleList,

    CnGold.getJinTouArticleLs,
    QHRB.getQHRBArticleList,
    Jinrongjie.getJinrongjieArticleList,
    AskCi.getAskCiArticleList,
    # SMM.getSMMArticleList,
    TongHua.getTongHuaArtList
]

pool=[]
for f in FuncList:
    #多线程
    # t=Thread(target=f,args=((articleCol,BeCrawledUrlList)))
    # t.start()
    # pool.append(t)

    #单线程
    f(articleCol,BeCrawledUrlList)

for t in pool:
    t.join()

    # try:
    #     pass
    # except Exception as e:
    #     print('有错误')
    #     print(e)
    #     os.system('pause')

##各自的文件存储完成后，汇总

print('总共 %d  条'%articleCol.count_documents({}))

#发送邮件
updateArticleList=[item  for item in articleCol.find({'mailed':False})]
print('本次更新 %d 条'%len(updateArticleList))
# from common import makeEmailHTML,sendEmail
# html=makeEmailHTML(updateArticleList)
   
# if sendEmail(html):
#     print('邮件发送成功') 
# else:
#     print('邮件发送失败+++++++++++++') 
#     os.system('pause')
# sleep(10)
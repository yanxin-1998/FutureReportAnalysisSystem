from uuid import uuid4
from time import sleep
import requests
sess=requests.session()
sess.headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}
def UID():
    uid = str(uuid4())  #通用唯一标识符
    suid = ''.join(uid.split('-'))   #处理完大概长这样f5563a572dbf4c2e9f4a473e9a4325a3
    return suid

def HandleTmpList(ls,col,From):
    count=0
    for item in ls:
        if bool(col.find_one({'url':item['url']})):  #看数据库collection中是否存在这个url的数据，findone返回找到的第一个
            print('重复',item['url'])
        else:
            item['mailed']=False
            col.insert_one(item)           #如若不存在则新增，并统计条数
            count+=1
        
    print('{} 新增 {} 条'.format(From,count))
    # if ls:
    #     col.insert_many(ls) 
    

ProductNameTuple=('苹果','红枣',
'原油','燃油',
'棉花','玉米','大豆','豆粕',
'橡胶',
'棕榈油','豆油','菜油',
'螺纹钢','焦炭','铁矿石','动力煤','焦煤',
'PTA','甲醇','乙二醇','苯乙烯',
'白糖','鸡蛋',
'镍','锌','铜','铅','铝',
'黄金','白银',
)
#品种别称
ProductNameDict={
'苹果':'苹果',
'红枣':'红枣',
'枣':'红枣',
'原油':'原油',
'石油':'原油',
'燃油':'燃油',
'燃料油':'燃油',
'棉花':'棉花',
'棉':'棉花',
'郑棉':'棉花',
'玉米':'玉米',
'大豆':'大豆',
'美豆':'大豆',
'豆粕':'豆粕',
'橡胶':'橡胶',
'沪胶':'橡胶',
'天胶':'橡胶',
'天然橡胶':'橡胶',
'合成橡胶':'橡胶',
'棕榈油':'棕榈油',
'棕油':'棕榈油',
'豆油':'豆油',
'菜油':'菜油',
'菜籽':'菜油',
'螺纹钢':'螺纹钢',
'钢铁':'螺纹钢',
'钢材':'螺纹钢',
'焦炭':'焦炭',
'冶金焦':'焦炭',
'铁矿石':'铁矿石',
'铁矿':'铁矿石',
'动力煤':'动力煤',
'焦煤':'焦煤',
'煤':'焦煤',
'PTA':'PTA',
'P聚酯':'PTA',
'甲醇':'甲醇',
'乙二醇':'乙二醇',
'EG':'乙二醇',
'苯乙烯':'苯乙烯',
'EB':'苯乙烯',
'尿素':'尿素',
'ur':'尿素',

'白糖':'白糖',
'糖':'白糖',
'鸡蛋':'鸡蛋',
'蛋':'鸡蛋',
'镍':'镍',
'锌':'锌',
'铜':'铜',
'铅':'铅',
'铝':'铝',
'金价':'黄金',
'白银':'白银',
}
groupToProduct= {
        '黑色系': ["螺纹钢", "焦炭", "铁矿石", "焦煤", "动力煤"],
        '有色': ["镍", "锌", "铜", "铅", "铝"],
        '化工': ["PTA", "甲醇", "乙二醇",'苯乙烯','尿素'],
        '农产品': ["苹果", "红枣", "棉花", "橡胶", "玉米", "白糖", "鸡蛋",'大豆','豆粕'],
        '能源': ["原油", "燃油"],
        '油脂': ["豆油", "棕榈油", "菜油"],
        '贵金属': ["黄金", "白银"]
      }
# GroupName=('黑色系','有色','化工','农产品','能源','油脂','贵金属')
GroupName=tuple([i for i in groupToProduct])
#品种到板块的映射
ProductToGroup={}
for group in groupToProduct:
    products_ls=groupToProduct[group]
    for product in products_ls:
        ProductToGroup[product]=group
# ProductToGroup={
# '苹果':'农产品',
# '红枣':'农产品',
# '棉花':'农产品',
# '橡胶':'农产品',
# '玉米':'农产品',
# '白糖':'农产品',
# '鸡蛋':'农产品',
# '大豆':'农产品',
# '豆粕':'农产品',

# '螺纹钢':'黑色系',
# '焦炭':'黑色系',
# '铁矿石':'黑色系',
# '焦煤':'黑色系',
# '动力煤':'黑色系',

# '镍':'有色',
# '锌':'有色',
# '铜':'有色',
# '铅':'有色',
# '铝':'有色',

# 'PTA':'化工',
# '甲醇':'化工',
# '乙二醇':'化工',
# '苯乙烯':'化工',

# '豆油':'油脂',
# '棕榈油':'油脂',
# '菜油':'油脂',

# '原油':'能源',
# '燃油':'能源',

# '黄金':'贵金属',
# '白银':'贵金属',

# }
# LongWord=('上涨','做多','多单持有','上行','','','','','','','','','','','','','',)
# ShortWord=()


def parseContentToName(content,ProductNameDict=ProductNameDict):
    '''
    根据文章内容，取得所属品种
    '''
    maxtimes=0
    freqWord=''
    for word in ProductNameDict:#统计每一个品种别称在文章中出现的次数，出现最多的那个就是本篇文章的所述品种
        m=content.count(word)
        if m>maxtimes:
            maxtimes=m
            freqWord=word
    ##品种别称映射统一名称
    if maxtimes==0:
        return ''
    return ProductNameDict[freqWord]

def makeEmailHTML(articleList:list) ->str:      #  : 表示参数类型，-> 表示返回值的类型
    '''
    构造邮件内容
    '''
    html=' '
    for item in articleList:
        item['publicTime']=item['publicTime'][:10]
        html+="<a href='{url}'>{product_name}-{title}-{publicTime}-{articleFrom}</a><br>".format(**item)

    return html


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def sendEmail(html):
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(html, 'html', 'utf-8')
    message['From'] = Header("cc9200@126.com")   # 发送者
    message['To'] =  Header("cc9200@126.com")        # 接收者

    subject = '今日财经资讯'     #主题
    message['Subject'] = Header(subject)
    smtp = smtplib.SMTP()
    smtp.connect("smtp.126.com")  # 发件人邮箱中的SMTP服务器，端口是25
    sender = 'cc9200@126.com'
    my_pass='cc15'  #邮箱的密码
    smtp.login(sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
    try:
        smtp.sendmail('cc9200@126.com',['cc9200@126.com'],message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        return True
    except:
        return False
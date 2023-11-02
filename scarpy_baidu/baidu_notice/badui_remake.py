'''
from lxml import etree
import pymysql
import json
import requests
baseurl_ajax='https://baike.baidu.com/cms/home/eventsOnHistory/{}.json'
head={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}

total_data_xpath='/html/body/div[2]/div/div[2]/div/div/dl/dd'
desc_xpath="/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/div[2]/div/span//text()"

def scarpy(url):
    html_text=requests.get(headers=head,url=url)
    return html_text.content.decode('utf-8')
def scarpy_html(url):
    html_text=scarpy(url)
    html=etree.HTML(html_text)
    return html
#def analysis_json先留着，看看能不能再把整个json的解析函数化
    
def scarpy_text(event_html):
    tree_desc=etree.HTML(event_html)#把html语言的文本转化为html标签，以供使用xpath，来获取所有text内容
    if tree_desc==None:
        return "空"
    desc_text_list=tree_desc.xpath("//text()")#返回了一个包含所有text的列表，把列表
    str_text ="".join(desc_text_list)
    str_text=str_text.replace("'","''")
    return str_text
def scarpy_desc(event_link):
    response_desc=scarpy_html(event_link)
    desc_text=response_desc.xpath(desc_xpath)
    a="".join(desc_text)
    b=a.replace("'","''")
    
    return b

def main_scarpy():#获取当当年每一天历史发生的重要事件,及其年份，类型，概述，
    
    for mon in range(1,13):#月份的遍历
        if mon<10:
            month='0'+str(mon)
        month_ajax_url='https://baike.baidu.com/cms/home/eventsOnHistory/%s.json'%(month)
        response=requests.get(headers=head,url=month_ajax_url)
        month_json=response.json()
        month=list(month_json.keys())[0]#这个月月份
        days_dict=month_json[month]#一个字典包含每天对应的历史事件 ，拿12月为例，‘首个’键值对是这样'1231':[... ],注意这个字典是倒序，第一个键值对是当月最后一天
        days=len(days_dict)#这个月天数
        for day in range(1,days+1):#日数的遍历
            if day<10:
                key_day='0'+str(day)
                key_day=month+key_day
            the_day_lievent=days_dict[key_day]#存放当天所有历史事件信息的列表，每一个元素为一个字典
            for single_event in the_day_lievent:#提取每一个单独事件，一个事件以字典形式存放,['#year', '#title', '#festival', 'link', '#type', '#desc', 'cover', 'recommend']这是一个事件字典所有键的名称，需要提取的这里打＃,每读完一次事件存储一次
                event_year=str(single_event['year'])#事件年份
                event_title=scarpy_text(single_event['title'])#事件标题，由于是html形式所以这边使用这个函数
                event_type=str(single_event['type'])#事件类型
                link_desc=single_event['link']#事件概要
                event_desc=scarpy_desc(link_desc)
                execute_insert_true="insert into history(year_event,title_event,type_event,desc_event) values('%s','%s','%s','%s')"%(event_year,event_title,event_type,event_desc)
                cur.execute(execute_insert_true)
                db.commit()


if __name__=="__main__":
    
    db=pymysql.connect(host='localhost',password='yby258014',user='root',database='today_in_history')
    cur=db.cursor()
    
    
    execute_create_table="create table history(year_event text,title_event text,type_event text,desc_event text)"
    #cur.execute(execute_create_table)
    try:
        cur.execute(execute_create_table)
    except:
        execute_drop="drop table history"
        cur.execute(execute_drop)
        print("该数据表已存在，故为您更新至最新")
        cur.execute(execute_create_table)
        main_scarpy()
        cur.close()
        db.close()
        
    else:
        main_scarpy()            
        cur.close()
        db.close()
''' 
import requests
from lxml import etree
import re
import json
import pymysql
pattern=r"[\u4e00-\u9fa5]"
pattern_2=r'\[.*?\]'
if __name__=='__main__':
    yea=[]
    db=pymysql.connect(host='localhost',user='root',password='yby258014',database='today_in_history')
    
    print('success')
    cur=db.cursor()
    execute_create_table="create table bd(year text,title text,type text,de text)"
    cur.execute(execute_create_table)
    headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69'
            }
    url='https://baike.baidu.com/cms/home/eventsOnHistory/0'+'%s'+'.json?_='
    num=1696082529004
    month=[31,29,31,30,31,30,31,31,30,31,30,31]
    for i in range(6):
        page_text = requests.get((url+str(num-i))%(str(i+1))).json()
        if i+1>10:
            l1=str(i+1)
        else:
            l1='0'+str(i+1)
        for j in range(month[i]):
            if j+1<10:
                l2=l1+'0'+str(j+1)
                c=page_text[l1][l2]
            else:
                l2=l1+str(j+1)
                c=page_text[l1][l2]
            for d in c:
                year=d['year']
                title=''.join(re.findall(pattern,d['title']))
                type_=d['type']
                desct=d['desc']
                if len(desct)!=0:
                    tree=etree.HTML(desct)
                    de=re.sub(pattern_2,'',''.join(tree.xpath('//text()'))).replace("'",'')
                    print(len(de))
                    sql = "insert into bd (year,title,type,de) values('%s','%s','%s','%s')"%(year, title, type_, de)
                    cur.execute(sql)
                    db.commit()
                else:
                    sql = "insert into bd (year,title,type,de) values('%s','%s','%s','%s')" % (year, title, type_, '')
                    cur.execute(sql)
    #cur.execute("delete from bd")
    db.commit()
    db.close()  
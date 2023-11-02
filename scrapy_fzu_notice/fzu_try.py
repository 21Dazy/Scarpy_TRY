import requests
import re
import json
import pymysql
from lxml import etree
import time
current_page=1

def scarpy(input_url):#返回一页的html文本内容
    response=requests.get(url=input_url,headers=head)
    return response.content.decode('utf-8')

def paqu_writer(data):#爬取一页中所有消息的通知人
    lresult=[]
    flag=0
    for n in data:
        for i in range(len(n)):
            if (n[i]=='【'):
                start=i+1
                flag=1
            if(n[i]=='】'):
                end=i
        if flag:
            lresult.append(n[start:end])
            flag=0
    return lresult

def paqu_time(data):#爬取消息时间
    lresult=[]
    for n in data:
        if re.match(pattern=pattern_time1,string=n):
            time_match=re.match(pattern=pattern_time1,string=n).group(1)
            lresult.append(time_match)
        if re.match(pattern=pattern_time2,string=n):
            time_match=re.match(pattern=pattern_time2,string=n)
            time_match=time_match.group(2)
            lresult.append(time_match)
    return lresult

def paqu_title(data):#爬取消息标题
    lresult=[]
    for i in range(0,len(data)):
        if re.match(pattern=pattern_time1,string=data[i]):
            continue
        if ('\r' in data[i] or '\n' in data[i]):
            continue
        lresult.append(data[i])
    return lresult   

def paqu_data(url_page):#爬取一页总的内容，以供拆解
    html_fzu=etree.HTML(scarpy(url_page))#转化为html标签内容，主要是为了使用xpath
    li=html_fzu.xpath(xpath_)
    return li

def paqu_detail_url(now_url):#爬取每个通知详情页的url
    detail_url_set=[]
    now_html=etree.HTML(scarpy(now_url))
    url_node=now_html.xpath(xpath_detail_url)#获取所有包含通知详情地址的节点
    for single_node in url_node:
        url="https://jwch.fzu.edu.cn/"+single_node.xpath("./a/@href")[0]#因为xpath查找出来的匹配对象会以列表形式返回，即使元素只有一个，所以要[0]来提取唯一的元素
        detail_url_set.append(url)
    return detail_url_set
def page_change(page):#当一页读完的时候，返回此页爬取的消息数，以及要读取的下一页的url,以列表的形式返回，l[0]为数量，l[1]为url
    if page==1:
        url='https://jwch.fzu.edu.cn/jxtz.htm'
    else:
        url=base_url+"/"+str(total_page-page+1)+".htm"
    next_url=base_url+"/"+str(total_page-page)+".htm"
    respone_data=paqu_data(url)
    nums=len(paqu_writer(respone_data))  
    return nums,next_url
     
base_url="https://jwch.fzu.edu.cn/jxtz"
new_url='https://jwch.fzu.edu.cn/jxtz.htm'#最新的通知主页

xpath_='/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div[1]/ul//text()'#用来或取一页里的所有通知
xpath_detail_url='/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div[1]/ul/li'
xpath_page='/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div[2]/div[1]/div/span[1]/span[9]/a/text()'


pattern_time1=re.compile('(\d{4}-\d{2}-\d{2})')
pattern_time2=re.compile('(\r\n)(\d{4}-\d{2}-\d{2})(\r\n)')
head={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}

html_fzu=etree.HTML(scarpy(new_url))#最新页面的html标签对象，用于之后的xpath查找

total_page=int(html_fzu.xpath(xpath_page)[0])

def main_scarpy(text_num,current_page=1):#爬取限定数量的通知，并以字典的形式返回,默认从最新一页开始爬
    current_url=new_url
    rest_num=text_num#剩余消息数，用于循环进行的判断
    total_lresult={"writers":[],"time":[],"title":[],"detail_url":[]}#初始化存放字典
    while rest_num>0:#一轮循环爬取一页，一次循环结束，合并一次数据
        current_data=paqu_data (current_url)
        if page_change(current_page)[0]<=rest_num:
            total_lresult["writers"]=total_lresult["writers"]+paqu_writer(current_data)
            total_lresult["time"]=total_lresult["time"]+paqu_time(current_data)
            total_lresult["title"]=total_lresult["title"]+paqu_title(current_data)
            total_lresult["detail_url"]=total_lresult["detail_url"]+paqu_detail_url(current_url)
        else:
            total_lresult["writers"]=total_lresult["writers"]+paqu_writer(current_data)[0:rest_num]
            total_lresult["time"]=total_lresult["time"]+paqu_time(current_data)[0:rest_num]
            total_lresult["title"]=total_lresult["title"]+paqu_title(current_data)[0:rest_num]
            total_lresult["detail_url"]=total_lresult["detail_url"]+paqu_detail_url(current_url)[0:rest_num]
        current_url=page_change(current_page)[1]
        rest_num=rest_num-page_change(current_page)[0]
        current_page=current_page+1
    return total_lresult    
if __name__=="__main__":
    
    db=pymysql.connect(host='localhost',user='root',password='yby258014',database='fzu_try')
    cur=db.cursor()
    num=int(input("请输入你要获取最近几条通知\n"))
    start=time.time()
    total_data=main_scarpy(num,1)
    table_name="fzu_notice_100"
    creat_excute='''
    create table fzu_notice_%d(
        writers text,
        time text,
        title text,
        detail_url text)
    '''%(num)
    try:
        cur.execute(creat_excute)
    except:
        print("当前数据表已经为您更新")
        drop_excute="drop table fzu_notice_%d"%(num)
        cur.execute(drop_excute)
        cur.execute(creat_excute)    
        lresult_val=[]
        values_base=list(total_data.values())
        keys=",".join(total_data.keys())
        key_list=list(total_data.keys())
        for i in range(num):
            for n in range(4):
                lresult_val.append(values_base[n][i])  
            insert_excute="insert into fzu_notice_%d(writers,time,title,detail_url) values('%s','%s','%s','%s')"%(num,lresult_val[0],lresult_val[1],lresult_val[2],lresult_val[3])
            cur.execute(insert_excute)
            lresult_val=[]
        db.commit()
        cur.close()
        db.close()
    else:
        print("已经为您获取最新的%d条通知内容"%(num))
        lresult_val=[]
        values_base=list(total_data.values())
        keys=",".join(total_data.keys())
        key_list=list(total_data.keys())
        print(len(values_base[3]))
        for i in range(num):
            for n in range(4):
                lresult_val.append(values_base[n][i]) 
            insert_excute="insert into fzu_notice_%d (writers,time,title,detail_url) values('%s','%s','%s','%s')"%(num,lresult_val[0],lresult_val[1],lresult_val[2],lresult_val[3])
            cur.execute(insert_excute)
            lresult_val=[]
        
        db.commit()
        end=time.time()
        cur.close()
        db.close()
        print(end-start)
    
    
    
    

import requests
import re
import json
import pymysql
from lxml import etree

current_page=1
def paqu_fujian_nums(list_download):#利用ajax请求,参数为下载地址的url,返回一个二维列表，一个小列表包含一个附件的两个参数,返回值是附件的xi[url1,url2]
    list_result=[]#存放每个ajax请求的参数
    base_parram={'type':'wbnewsfile','randomid':'nattach','wbnewsid':0,'owner':0}
    list_download_nums=[]
    for base in list_download:
        parram_owner=re.match(pattern=pattern_parrams,string=base).group(1)
        parram_wbnewsid=re.match(pattern=pattern_parrams,string=base).group(2)
        base_parram['owner']=parram_owner
        base_parram['wbnewsid']=parram_wbnewsid
        list_result.append(base_parram)
        base_parram={'type':'wbnewsfile','randomid':'nattach','wbnewsid':0,'owner':0}
    for i in list_result:
        response=requests.get(headers=head,url=fujian_download_baseurl,params=i).json()
        list_download_nums.append(response['wbshowtimes'])
    return list_download_nums
    
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
def paqu_fujian(page_url):#爬取附件的下载地址，名称,下载次数
    content=scarpy(page_url)
    list_download=[]
    list_biaoti=[]
    if "附件【" in content:
        
        list_download=re.findall(pattern_fujian_download,content,re.S)
        list_biaoti=re.findall(pattern_fujian_name,content,re.S)
        list_nums=paqu_fujian_nums(list_download)
        return list_download,list_biaoti,list_nums
    else:
        
        return  0
        
    
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
fujian_download_baseurl='https://jwch.fzu.edu.cn/system/resource/code/news/click/clicktimes.jsp'

xpath_='/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div[1]/ul//text()'#用来或取一页里的所有通知
xpath_detail_url='/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div[1]/ul/li'
xpath_page='/html/body/div[1]/div[2]/div[2]/div/div/div[3]/div[2]/div[1]/div/span[1]/span[9]/a/text()'
xpath_fujian='/html/body/div/div[2]/div[2]/form/div/div[1]/div/ul//text()'

fujian_dict={'detail_title':[],'down_url':[],'biaoti':[],'download_times':[]}
pattern_time1=re.compile('(\d{4}-\d{2}-\d{2})')
pattern_time2=re.compile('(\r\n)(\d{4}-\d{2}-\d{2})(\r\n)')
pattern_fujian_download=r'<li>附件.*?href="(/system/.*?download.jsp.*?wbfileid=\d{1,})"'#附件的下载地址
pattern_fujian_name=r'<li>附件.*?href=.*?附件\d：(.*?)</a>'
pattern_parrams=r'.*?owner=(\d+)&wbfileid=(\d+)'
head={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
html_fzu=etree.HTML(scarpy(new_url))#最新页面的html标签对象，用于之后的xpath查找
total_page=int(html_fzu.xpath(xpath_page)[0])
def sql_fujian(dict):
    total=[]
    
    for i in dict:
        single=(dict[i])
        
    
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
    for i in range(len(total_lresult['detail_url'])):
        detail_url=total_lresult['detail_url'][i]
        detail_title=total_lresult['title'][i]
        if paqu_fujian(detail_url):
            fujian_dict['detail_title']=fujian_dict['detail_title']+[detail_title]
            fujian_dict['down_url']=fujian_dict['down_url']+paqu_fujian(detail_url)[0]
            fujian_dict['biaoti']=fujian_dict['biaoti']+paqu_fujian(detail_url)[1]
            fujian_dict['download_times']=fujian_dict['download_times']+paqu_fujian(detail_url)[2]
    return total_lresult    
if __name__=="__main__":
    #fl=open("page_text.html",'w+',encoding="utf-8")
    #fl.write(scarpy('https://jwch.fzu.edu.cn/info/1036/13034.htm'))
    main_scarpy(10)
    for i in range(fujian_dict['biaoti']):
        
        insert_excute="insert into fzu_fujian_%d (writers,time,title,detail_url) values('%s','%s','%s','%s')"%(fujian_dict['detail_title'][i],fujian_dict['down_url'][i],fujian_dict['biaoti'][i],fujian_dict['download_times'][i])
        cur.execute


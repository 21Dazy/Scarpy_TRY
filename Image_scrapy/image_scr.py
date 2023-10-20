#本程序目的，是输入一个特定的网址，将爬取的图片进行持久化存储
import os
import requests
import re
import time
head={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
pattern_png=r'//.*?.png'
pattern_jpg=r'//.*?.jpg'
pattern_gif=r'//.*?.gif'
def scarpy_text(url):#参数为该网站url
    response=requests.get(url=url,headers=head)
    return response.text
def scarpy_content(url):
    response=requests.get(url=url,headers=head)
    return response.content
def main_image_scarpy(baseurl):#输入参数为该网址的url
    content_base=scarpy_text(baseurl)
    listjpg=re.findall(pattern_jpg,content_base,re.S)
    listpng=re.findall(pattern_png,content_base,re.S)
    listgif=re.findall(pattern_gif,content_base,re.S)
    for i in range(len(listjpg)):
        time.sleep(2.5)
        img_url='https:'+listjpg[i]
        img_data=scarpy_content(img_url)
        with open('./Image/'+'%d.jpg'%(i),'wb') as fl:
            fl.write(img_data)
            print('该图片已保存')
    for j in range(len(listpng)):
        time.sleep(2.5)
        img_url='https:'+listjpg[j]
        img_data=scarpy_content(img_url)
        with open('./Image/'+'%d.png'%(j),'wb') as fl:
            fl.write(img_data)
            print('该图片已保存')
    '''       
    for k in range(len(listgif)):
        time.sleep(3)
        img_url='https:'+listgif[j]
        img_data=scarpy_content(img_url)
        with open('./Image/'+'%d.gif'%(k),'wb') as fl:
            fl.write(img_data)
            print('该图片已保存')
    '''
if __name__=='__main__':
    print("请输入你要的网址\nps:本爬虫只支持jpg和png格式\n")
    if not os.path.exists('./Image'):
        os.mkdir('./Image')
    baseurl=input()
    main_image_scarpy(baseurl)
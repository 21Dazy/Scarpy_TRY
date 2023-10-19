import os
import requests
import re

url='https://www.bilibili.com/read/cv7011412/?from=search&spm_id_from=333.337.0.0'

head={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
url_ex='https://i0.hdslb.com/bfs/article/0ddd1e3689629d06b7866a1ef88b1790ff3ee89f.jpg'
pattern_image=re.compile('<img data-src="(.*?.jpg)@.*?"')
if __name__=="__main__":
    
    response=requests.get(url=url,headers=head)
    response_text=response.text#获取网页源码，用于解析
    ex='<img data-src="(.*?jpg).*?'
    image_list=re.findall(ex,response_text,re.S)
    listimg=[]
    a='//i0.hdslb.com/bfs/article/ec179dd36dc1fa2ee2a28f94762dda0374eabe64.jpg'
    for i in image_list:
        if re.match(pattern=r'.*?.jpg',string=i):
            
            listimg.append(i)
            
            
    
    for img in listimg:
        img_url="https:"+img+'?'
        
        img_data=requests.get(url=img_url,headers=head).content
        with open('./Image/'+'%s.jpg'%(input()),'wb') as tu:
            tu.write(img_data)
            print('图片已经保存')
    
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time       : 2020/9/19
# @Author     : Rye

# 【代码说明】
# 代码收集豆瓣帖子信息，分四个Sheet收集以下信息，并保存至本地Excel：
# ○ Sheet1 主楼信息：楼主name，主页url，标题，帖子url，总评论数，评论热赞数，总点赞数，总转发数，开贴时间，所在小组，小组url，
#                   主楼内容，主楼图片/视频，爬帖时间
# ○ Sheet2 跟帖信息：跟帖name，主页url，获赞数，跟帖时间，跟帖内容（前5条为热赞，其余按时间顺序排列），是否为回复楼中楼，楼中楼被回复人主页
# ○ Sheet3 点赞信息：点赞name，主页url，点赞时间
# ○ Sheet4 转发信息：转发name，主页url，转发时间，转发内容

# 【操作说明】
# 使用时输入豆瓣帖子网址即可，请一定包含最后面的"/"。格式举例：https://www.douban.com/group/topic/12345/
# 程序运行完成后，收集信息自动保存在本地Excel中，文件名为：开帖日期-时间_爬帖日期-时间_豆瓣小组名_帖子网址id_帖子标题.xlsx
# 考虑到隐私侵权和多次访问风险，代码在非登录状态下爬虫，因此暂不适用于 私密组 或 处于停用or雪藏期的公共组 帖子。

# 1 Preparation

print('='*56,'\n@ Filename: 豆瓣帖子信息收集_public.exe\n'
             '@ Author  : Rye\n'
             '@ Pub Date: 2020/09/27\n'
             '@ Version : 1.1')

print('\n===================== 【代码说明】 =====================\n'
      '代码收集豆瓣帖子信息，分四个Sheet收集以下信息，并保存至本地Excel：\n'
      '○ Sheet1 主楼信息：楼主name，主页url，标题，帖子url，总评论数，评论热赞数，总点赞数，总转发数，'
                        '开贴时间，所在小组，小组url，主楼内容，主楼图片/视频，爬帖时间\n'
      '○ Sheet2 跟帖信息：跟帖name，主页url，获赞数，跟帖时间，跟帖内容（前5条为热赞，其余按时间顺序排列），'
                        '是否为回复楼中楼，楼中楼被回复人主页\n'
      '○ Sheet3 点赞信息：点赞name，主页url，点赞时间\n'
      '○ Sheet4 转发信息：转发name，主页url，转发时间，转发内容\n')

print('\n===================== 【操作说明】 =====================\n'
      '（1）按程序提示输入豆瓣帖子网址即可，请一定包含最后面的“/”。格式举例：https://www.douban.com/group/topic/12345/\n'
      '（2）程序运行完成后，所收集信息自动保存至本地Excel，文件名为：开帖日期-时间_爬帖日期-时间_豆瓣小组名_帖子网址id_帖子标题.xlsx\n'
      '（3）考虑到隐私侵权和多次访问风险，代码在非登录状态下爬虫，因此暂不适用于【私密组】或【处于停用or雪藏期的公共组】帖子（´◔﹏◔）')

print('='*56,'\n>> 程序开始！')

import pandas as pd
import numpy as np
import datetime
import requests
from bs4 import BeautifulSoup
import json

import random
import time
import re

import getproxies


# 2 Function Design
# （非登录状态爬虫）
# （1）转评赞收集函数
# 提取以下信息：
# 跟帖人    【name，主页url，获赞数，跟帖时间，跟帖内容，回复楼中楼，被回复人主页】(sub="cmt")  
# 主楼点赞人【name，主页url，点赞时间】 (sub="like")
# 转发人    【name，主页url，转发时间，转发内容】(sub="rec")

def get_subinfo(item, sub, vote_dict=None):
    if( sub == "like" or sub == "rec"):
        reply_name = item.find('a',class_="").get_text()
        reply_id = item.find('a',class_="").get("href")
        reply_time = item.find('span', class_="pubtime").get_text()
        if sub == "like": 
            return reply_name,reply_id, reply_time
        else:
            try: reply_text = item.find('p').get_text().strip('\n')
            except: reply_text = ""
            return reply_name, reply_id, reply_time, reply_text
    # 跟帖
    else:
        reply_name = item.find_all('a',class_="")[1].get_text()
        reply_id = item.find_all('a',class_="")[1].get('href')
        reply_time = item.find('span', class_="pubtime").get_text()
        reply_text = item.find('p', class_="reply-content").get_text()
        # 楼中楼
        try:
            reply_reply = item.find('span', class_="all").get_text()
            reply_reply_id = item.find('span', class_="pubdate").find('a').get("href")
        except: reply_reply_id=""; reply_reply=""
        # 提取 赞数
        pattern = re.compile(r'\d+')
        pos = re.search("data-cid=",str(item)).span()[-1]
        vote_id = 'c' + pattern.findall(str(item)[pos:pos+15])[0]    
        try: vote_num = vote_dict[vote_id]   # 有获赞
        except: vote_num = 0
        return reply_name,reply_id, reply_time, vote_num, reply_text, reply_reply_id, reply_reply


# （2）转评赞页访问函数
def get_subpage(post_url, sub, proxies ,login_data=None):
    sub_url = post_url + "?type=%s"%sub
    #response = requests.get(sub_url,headers=headers, timeout=5)
    proxies = proxies
    response = requests.get(sub_url, headers=headers, proxies=proxies, timeout=10)

    if not response.status_code == 200: print('      ！Error:',response.status_code)
    results_page = BeautifulSoup(response.content,'lxml')
    
    # 转评赞总页数
    try: page_num = int(results_page.find('div', class_="paginator").find_all('a')[-2].get_text())
    except: page_num = 1

    if sub=="like": tag="点赞"
    elif sub=="rec": tag="转发"
    else: tag="评论"

    name_list=[]; id_list=[]; time_list=[]; votenum_list=[]; text_list=[]; reply_rplid_list=[]; reply_rpl_list=[]
    # 访问页面，收集信息
    for p in range(page_num):
        print("      ",tag,"收集第",p+1,"页...")
        try:
            if sub =="rec": url = sub_url + '&start=%d'%(30*p)
            else: url = sub_url + '&start=%d'%(100*p)
            response = requests.get(url,headers=headers)
            if not response.status_code == 200: print('      ！',tag,'第',p+1,'页：Error Code',response.status_code)
            results_page = BeautifulSoup(response.content,'lxml')
        except: print('      ！',tag,'第',p+1,'页：Page Request Error')
        # 点赞页
        if sub=="like":
            cmt_page = results_page.find('div', class_="list topic-fav-list").find_all('div', class_="content")
            if len(cmt_page)==0: print('      帖子当前无点赞。')
            else:
                for item in cmt_page:
                    try:
                        reply_name, reply_id, reply_time = get_subinfo(item, "like", vote_dict=None)
                        name_list.append(reply_name); id_list.append(reply_id); time_list.append(reply_time)
                    except: print("      ！点赞爬取Error");continue
        # 转发页
        elif sub=="rec":
            cmt_page = results_page.find('div', class_="list topic-rec-list").find_all('div', class_="content")
            if len(cmt_page)==0: print('      帖子当前无转发。')
            else:
                for item in cmt_page:
                    try:
                        reply_name, reply_id, reply_time, reply_text = get_subinfo(item, "rec", vote_dict=None)
                        name_list.append(reply_name); id_list.append(reply_id); time_list.append(reply_time); text_list.append(reply_text)
                    except: print("      ！转发爬取Error");continue
        # 跟帖页               
        else:
            cmt_page = results_page.find_all('li', class_="clearfix comment-item reply-item")
            if len(cmt_page)==0: print('      帖子当前无回复。')
            else:
                # 跟帖获赞数（先获取当前页面总点赞数汇总dict）
                for ss in results_page.find_all('script',{'type': None }):
                    if "commentsVotes" in str(ss.get_text):
                        #ss = str(ss).lstrip('<script>').rstrip('</script>>')
                        vote_dict = json.loads(str(ss).split("commentsVotes")[1].split("\'")[1]); break

                # 爬取各楼层跟帖人信息
                for item in cmt_page:
                    try:
                        reply_name,reply_id,reply_time,vote_num,reply_text,reply_reply_id,reply_reply = get_subinfo(item,"cmt",vote_dict)
                        name_list.append(reply_name); id_list.append(reply_id); time_list.append(reply_time); votenum_list.append(vote_num);
                        text_list.append(reply_text); reply_rplid_list.append(reply_reply); reply_rpl_list.append(reply_reply_id)
                    except: print("      ！评论爬取Error");continue

    if sub=="like":  REPLY_INFO = [name_list, id_list, time_list]
    elif sub=="rec": REPLY_INFO = [name_list, id_list, time_list, text_list]
    else:            REPLY_INFO = [name_list, id_list, votenum_list, time_list, text_list, reply_rplid_list, reply_rpl_list]

    return REPLY_INFO

def check_proxy_avaliability(proxy):
    url = 'https://baidu.com/'
    result = open_url_using_proxy(url, proxy)
    VALID_PROXY = False
    if result:
        r, status_code = result
        text = r.text
        if status_code == 200:
            r_title = re.findall('<title>.*</title>', text)
            if r_title:
                if r_title[0] == '<title>百度一下，你就知道</title>':
                    VALID_PROXY = True
        if VALID_PROXY:
            check_ip_url = 'https://jsonip.com/'
            try:
                r, status_code = open_url_using_proxy(check_ip_url, proxy)
            except:
                return

            print('有效代理IP: ' + str(proxy))
            return True
    else:
        return False
        print('无效代理IP: ' + str(proxy))

def open_url_using_proxy(url, proxy):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
#    headers = {'User-Agent': user_agent}
    proxies = {}
    proxies['https'] = proxy
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return (r, r.status_code)
    except:
        print('无法访问网页' + url)
        print('无效代理IP: ' + proxy)
        return False


# （3）主函数
def main_collect(post_url ,proxies):
    global sess, headers
    sess = requests.session()
    proxies =proxies
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    login_data=None
    #proxies = {
    #    "https": "103.153.40.38:8080"
    #}
    #check_proxy_avaliability(proxies)
    '''
    # ====================== *以下为登录页判断* ======================
    try:
        url_temp = post_url
        #response = requests.get(url_temp,headers=headers, timeout=5)
        response = requests.get(url_temp,headers=headers, proxies=proxies, timeout=10)
        if not response.status_code == 200:
            print("response.status_code=====" + response.status_code)
            sec = input("该帖是否属于【私密组】或【处于停用or雪藏期的公共组】？请输入【是/否】：").strip()
            if sec == "是": print("   ！无法进入私密小组！请换公共组帖子重试"); return
            else:            
                print('   ！Error！请再次检查上述问题是否输入正确！若输入正确，则为网页请求错误，Error Code:',response.status_code); return
    except: print('   ！Secret Main Page Request Error')
    '''
    # ====================== *以下为爬虫页* ====================== 
    try:
        url = post_url

        #response = requests.get(url,headers=headers, timeout=5)
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)

        if not response.status_code == 200:
            print('   ！Error:',response.status_code)
            return False
        results_page = BeautifulSoup(response.content,'lxml')
    except: print('   ！Regular Main Page Request Error')
        
    # 1 【主楼信息】
    # 楼主name，主页url
    post_name = results_page.find('span',class_="from").find('a').get_text()
    post_id = results_page.find('span',class_="from").find('a').get('href')
    
    # 热赞数
    try: hot_vote = len(results_page.find('ul', class_="topic-reply popular-bd"))//2
    except: hot_vote = 0
    # 标题，帖子url，总评论数，开贴时间
#    script0 = results_page.find('script', {'type': 'application/ld+json'}).get_text()
    script0 = results_page.find('script', {'type': 'application/ld+json'}).get_text
    script0 = str(script0).lstrip('<bound method Tag.get_text of <script type="application/ld+json">').rstrip('</script>>')
    try: script = json.loads(script0, strict=False)
    except: script = json.loads(re.sub(r"\n|\t|\r|\r\n|\n\r|\x08|\\", "", script0), strict=False)
    title = script["name"]
    post_url = script["url"]
    cmt_num = script["commentCount"]
    post_date = script["dateCreated"].replace("T"," ")        
    # 主楼文字内容
    try: post_text = results_page.find('div', class_="rich-content topic-richtext").get_text()
    except: print("      主楼无文字。"); post_text=""
    # 主楼图片，视频
    post_links=[]
    try: 
        imgs = results_page.find('div', class_="rich-content topic-richtext").find_all('img')    
        videos = results_page.find('div', class_="rich-content topic-richtext").find_all('iframe')
        for m in (imgs+videos):
            pic = m.get('data-original-url')
            if pic==None: pic = m.get('src')
            post_links.append(pic)
    except: print("      主楼无图片视频。")
    # 所在小组
    group = results_page.find('div',class_="title").find('a').get_text()
    group_url = results_page.find('div',class_="title").find('a').get('href')

    # 2【跟帖信息】
    REPLY_INFO = get_subpage(post_url, "cmt", proxies, login_data )
    # 3【点赞信息】
    LIKE_INFO = get_subpage(post_url, "like", proxies, login_data)
    # 4【转发信息】
    REC_INFO = get_subpage(post_url, "rec", proxies, login_data)
    
    cmt_num = len(REPLY_INFO[0])-hot_vote       # 修正总评论数：子list中前x条为热赞
    like_num = len(LIKE_INFO[0])
    rec_num = len(REC_INFO[0])
    
    # 【主楼信息】：楼主name，主页url，标题，帖子url，总评论数，评论热赞数，总点赞数，总转发数，开贴时间，所在小组，小组url，主楼内容，主楼图片/视频】
    POST_INFO = [post_name, post_id, title, post_url, cmt_num, hot_vote, like_num, rec_num, post_date,
                 group, group_url, post_text, post_links]
    
    return POST_INFO, REPLY_INFO, LIKE_INFO, REC_INFO



if __name__ == '__main__':

    e_path = r'D:\zhoushen\99-记录\未爬取.xlsx'
    data_frame = pd.ExcelFile(e_path)
    eurl = data_frame.parse('Sheet1')
    urllist = eurl['link']
    proxies = {}
    # 3 开始信息收集
    #post_url = input("请输入豆瓣帖子网址【请一定包含最后面的“/”】：").strip()
    proxy_ip_filename = 'proxy_ip.txt'
    text = open(proxy_ip_filename, 'r', encoding='gb18030').read()
    proxy_ip_list = getproxies.get_proxy_ip(text)
    for proxy in proxy_ip_list:
        if check_proxy_avaliability(proxy):
            proxies['https'] = proxy
            for post_url in urllist:

                try: POST_INFO, REPLY_INFO, LIKE_INFO, REC_INFO= main_collect(post_url, proxies)
                except Exception as e: print("\n\n",e); print("\n>> 错误，请按任意键退出..." + post_url)

                collect_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                POST_INFO.append(collect_time)
                print('>> 收集完成！')


                # 可视化 dataframe
                # （1）主楼
                df_post = pd.DataFrame(POST_INFO,index=['楼主Name','主页url','标题','帖子url','总评论数','评论热赞数','总点赞数','总转发数',
                                                        '开贴时间','所在小组','小组url','主楼内容','主楼图片/视频','帖子爬取时间'])
                pd.set_option('display.unicode.east_asian_width', True)
                pd.set_option('display.colheader_justify', 'left')
                print("\n======= 主楼信息 =======\n", df_post)

                # （2）跟帖楼
                df_ori = pd.DataFrame(REPLY_INFO,index=['跟帖name','主页url','获赞数','跟帖时间','跟帖内容','回复楼中楼','被回复人主页'])
                df_reply = pd.DataFrame(df_ori.values.T, index=df_ori.columns, columns=df_ori.index)#转置
                # 检查评论是否收集完整
                if len(df_reply) == int(df_post.loc["总评论数"].values[0])+df_post.loc["评论热赞数"].values[0]: print('>> 评论收集完整！')
                pd.set_option('display.unicode.east_asian_width', True)
                pd.set_option('display.colheader_justify', 'left')
                pd.set_option('expand_frame_repr', False)
                print("\n======= 跟帖信息 ======= \n", df_reply.head(7))

                # （3）点赞楼
                df_oril = pd.DataFrame(LIKE_INFO,index=['点赞name','主页url','点赞时间'])
                df_like = pd.DataFrame(df_oril.values.T, index=df_oril.columns, columns=df_oril.index)
                print("\n======= 点赞信息 ======= \n", df_like.head(3))

                # （4）转发楼
                df_orir = pd.DataFrame(REC_INFO,index=['转发name','主页url','转发时间','转发内容'])
                df_rec = pd.DataFrame(df_orir.values.T, index=df_orir.columns, columns=df_orir.index)
                print("\n=======  转发信息 ======= \n", df_rec.head(5))



                # 4 将信息存入Excel，分四个Sheet分别存放

                try: group_name = df_post.loc["所在小组"].values[0][2:4]
                except: group_name = df_post.loc["所在小组"].values[0]
                pattern = re.compile(r'topic/\d+')
                post_id = pattern.findall(post_url)[0][6:]
                exl_name = "开帖"+df_post.loc["开贴时间"].values[0][5:-3].replace("-","").replace(":","").replace(" ","-")\
                           +'_爬帖'+df_post.loc["帖子爬取时间"].values[0][5:-3].replace("-","").replace(":","").replace(" ","-")\
                           +'_'+group_name+'_'+post_id+'_'+df_post.loc["标题"].values[0][:10]+'.xlsx'

                spe_list = list(set('\/:*?"<>|').intersection(set(exl_name)))
                if spe_list!=[]:    # 替换特殊字符 \/:*?"<>|
                    for s in spe_list: exl_name = exl_name.replace(s,"_")

                writer = pd.ExcelWriter(exl_name)
                df_post.to_excel(writer, sheet_name='主楼信息', header=True,index=True)
                df_reply.to_excel(writer, sheet_name='跟帖信息', header=True,index=True)
                df_like.to_excel(writer, sheet_name='点赞信息', header=True,index=True)
                df_rec.to_excel(writer, sheet_name='转发信息', header=True,index=True)
                writer.save()
                writer.close()

                print('\n')
                print('='*56,"\n>> 程序完成！！帖子信息已保存至本地文件:",exl_name)
                ##input(">> 请按任意键退出...")
                #sleep_time = random.randint(10, 15)
                #time.sleep(sleep_time)
            else:
                continue
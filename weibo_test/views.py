#!/usr/bin/python
#coding=utf-8

import sys
reload (sys)
sys.setdefaultencoding("utf-8")

import json
import numpy as np
from weibo import APIClient
from django.http import HttpResponse
from django.shortcuts import render_to_response

#0--话题制造
#1--意见领袖
#2--名人效应
#3--分享主导
#4--原创主导
#5--偏好潜水
#6--极端边缘
#7--其他

#------用户类型识别函数------
def IdentifyUserRole(originalActivity, transportActivity, transAbility, fansNumber, concernNumber):
    if originalActivity <= 0 and transportActivity <=0 and transAbility <=0:
        role = 7
    else:
        if originalActivity <= 4.6051:
            if transportActivity <= 4.6051:
                if fansNumber <= 11.5129:
                    if concernNumber <= 4.6051:
                        role = 6
                    else:
                        role = 5
                else:
                     role = 2
            else:
                if transportActivity <= 5.2983 or  fansNumber <= 9.2103 or transAbility <=8.1886:
                    if fansNumber <= 11.5129:
                        role = 3
                    else:
                        role = 2
                else:
                    role = 1
        else:
            if originalActivity - transportActivity <=0.6931:
                if transportActivity <= 5.2983 or  fansNumber <= 9.2103 or transAbility <=8.1886:
                    if fansNumber <= 11.5129:
                        role = 3
                    else:
                        role = 2
                else:
                    role = 1
            else:
                if originalActivity <= 5.2983 or fansNumber <= 8.0064 or transAbility <=8.1886:
                    if fansNumber <= 11.5129:
                        role = 4
                    else:
                        role = 2
                else:
                    role = 0
    return str(role)    
#生成oauth授权的url
def login(request):

    APP_KEY = 'XXXX'
    APP_SECRET = 'XXXXXXXXXXX'
    CALLBACK_URL = 'XXXXX'

    client = APIClient(app_key=APP_KEY,app_secret=APP_SECRET,redirect_uri=CALLBACK_URL)
    login_url = client.get_authorize_url()
    return render_to_response('login.html',{'login_url':login_url})

#用户oauth授权之后跳转到test页面
def test(request):

    APP_KEY = 'XXXX'
    APP_SECRET = 'XXXXXXXXXXXXX'
    CALLBACK_URL = 'XXXX'

    #获取access token
    client = APIClient(app_key=APP_KEY,app_secret=APP_SECRET,redirect_uri=CALLBACK_URL)
    code = request.GET['code']
    r = client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    client.set_access_token(access_token,expires_in)

    #获取用户uid
    user_id = client.account__get_uid()['uid']

    #获取用户粉丝数关注数和微博总数
    user_counts = client.get.users__counts(uids=int(user_id))[0]
    followers = int(user_counts['followers_count'])
    friends = int(user_counts['friends_count'])
    statuses = int(user_counts['statuses_count'])
    #获取用户原创的微博总数和转发的微博总数
    transPost = int(client.get.statuses__repost_by_me()['total_number'])
    originalPost = int(statuses)-int(transPost)
    #获取微博的转发数
    statuse_ids = client.get.statuses__user_timeline__ids(count=100,since_id=0,uid=int(user_id))['statuses']
    para = ','.join(statuse_ids)
    noTransPost = 0
    beTransPost = 0
    beTransNumber = 0
    for a in client.get.statuses__count(ids=para):
        if a['reposts'] == 0:
            noTransPost += 1
        else:
            beTransPost += 1
            beTransNumber += int(a['reposts'])

    #Calculate characteristics
    if originalPost != 0:
        original_percent = (originalPost * 100)/(originalPost + transPost)
        originalActivity = np.log(original_percent * statuses / 100)#用微博总数计算
    else:
        originalActivity = 0
        original_percent = 0
    if transPost != 0:
        transportActivity = np.log((100-original_percent) * statuses / 100)#用微博总数计算
    else:
        transportActivity = 0
    if beTransPost != 0:
        transAbility = np.log(float(beTransPost)/(originalPost+transPost) * float(beTransNumber)/beTransPost * 1000)
        be_trans_percent = (beTransPost * 100)/(originalPost+transPost)
        avg_be_trans_number = float(beTransNumber)/beTransPost
    else:
        transAbility = 0
        be_trans_percent = 0
        avg_be_trans_number = 0
    if followers != 0:
        fansNumber = np.log(followers)
    else:
        fansNumber = 0
    if friends != 0:
        concernNumber = np.log(friends)
    else:
        concernNumber = 0
    
    role = IdentifyUserRole(originalActivity,transportActivity,transAbility,fansNumber,concernNumber)
    return render_to_response('test.html',{'followers':followers,'friends':friends,'statuses':statuses,'original':originalPost,'repost':transPost,'a':role})

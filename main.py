import time,json,requests,random,datetime
from campus import CampusCard

def main():
    #校内校外开关
    mark = 1
    #定义变量
    success,failure=[],[]
    #sectets字段录入
    phone, password, sckey = [], [], []
    #多人循环录入
    while True:  
        try:
            users = input()
            info = users.split(',')
            phone.append(info[0])
            password.append(info[1])
            sckey.append(info[2])
        except:
            break

    #提交打卡
    for index,value in enumerate(phone):
        print("开始尝试为用户%s打卡"%(value[-4:]))
        count = 0
        while (count <= 3):
            try:
                campus = CampusCard(phone[index], password[index])
                token = campus.user_info["sessionId"]
                userInfo=getUserInfo(token)
                if mark == 0:
                    response = checkIn(userInfo,token)
                if mark == 1:
                    ownPhone=phone[index]
                    response = check(ownPhone,userInfo,token)
                strTime = getNowTime()
                if response.json()["msg"] == '成功':
                    success.append(value[-4:])
                    print(response.text)
                    msg = strTime + value[-4:]+"打卡成功"
                    if index == 0:
                        result=response
                    break
                else:
                    failure.append(value[-4:])
                    print(response.text)
                    msg =  strTime + value[-4:] + "打卡异常"
                    count = count + 1
                    if index == 0:
                        result=response
                    if count<=3:
                        print('%s打卡失败，开始第%d次重试...'%(value[-4:],count))
                    time.sleep(5)
            except Exception as e:
                print(e.__class__)
                failure.append(value[-4:])
                strTime = getNowTime()
                msg = strTime + value[-4:] +"出现错误"
                count = count + 1
                if index == 0:
                    result=response
                if count<=3:
                    print('%s打卡出错，开始第%d次重试...'%(value[-4:],count))
                time.sleep(1)
        print(msg)
        print("-----------------------")
    fail = sorted(set(failure),key=failure.index)
    title = "成功: %s 人,失败: %s 人"%(len(success),len(fail))
    try:
        print('主用户开始微信推送...')
        wechatPush(title,sckey[0],success,fail,result)
    except:
        print("微信推送出错！")

#时间函数
def getNowTime():
    cstTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=8))
    strTime = cstTime.strftime("%H:%M:%S ")
    return strTime

#信息获取函数
def getUserInfo(token):
    token={'token':token}
    sign_url = "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo"
    #提交打卡
    response = requests.post(sign_url, data=token)
    return response.json()['userInfo']

#校内打卡提交函数
def checkIn(userInfo,token):
    sign_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
     #随机温度(36.2~36.8)
    a=random.uniform(36.2,36.8)
    temperature = round(a, 1)
    jsons=   {"businessType": "epmpics", "method": "submitUpInfo",
         "jsonData": {"deptStr": {"deptid": 146141, "text": "数学与计算机科学学院-计算机科学与技术-计算机科学与技术2018级（3）班"},
                      "areaStr": "{\"streetNumber\":\"\",\"street\":\"\",\"district\":\"钟山区\",\"city\":\"六盘水市\",\"province\":\"贵州省\",\"town\":\"\",\"pois\":\"六盘水师范学院(龙山校区)\",\"lng\":104.82745899999946,\"lat\":26.575612979920976,\"address\":\"钟山区六盘水师范学院(龙山校区)\",\"text\":\"贵州省-六盘水市\",\"code\":\"\"}",
                      "reportdate": 1610633613104, "customerid": "2864", "deptid": 146141, "source": "app",
                      "templateid": "pneumonia", "stuNo": "184006023018", "username": "母成吉", "phonenum": "",
                      "userid": "24737345", "updatainfo": [{"propertyname": "langtineadress", "value": "楷院"},
                                                           {"propertyname": "wendu", "value": "36.3"},
                                                           {"propertyname": "symptom", "value": "无症状"},
                                                           {"propertyname": "isConfirmed", "value": "否"},
                                                           {"propertyname": "isdefinde", "value": "否.未隔离"},
                                                           {"propertyname": "isGoWarningAdress", "value": "否"},
                                                           {"propertyname": "isTouch", "value": "否"},
                                                           {"propertyname": "isTransitArea", "value": "否"},
                                                           {"propertyname": "isTransitProvince", "value": "否"},
                                                           {"propertyname": "isFFHasSymptom", "value": "没有"},
                                                           {"propertyname": "isContactFriendIn14", "value": "没有"},
                                                           {"propertyname": "xinqing", "value": "健康"},
                                                           {"propertyname": "cxjh", "value": "否"},
                                                           {"propertyname": "isleaveaddress", "value": "否"},
                                                           {"propertyname": "dormitory", "value": "楷苑"},
                                                           {"propertyname": "isAlreadyInSchool", "value": "有"},
                                                           {"propertyname": "ownPhone", "value": "18885422645"},
                                                           {"propertyname": "emergencyContact", "value": "母成吉"},
                                                           {"propertyname": "mergencyPeoplePhone",
                                                            "value": "18885422645"},
                                                           {"propertyname": "assistRemark", "value": ""}], "gpsType": 1,
                      "token": token}}
    #提交打卡
    response = requests.post(sign_url, json=jsons)
    return response

#校外打卡
def check(ownPhone,userInfo,token):
    sign_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
    #获取datajson
    post_json = {
            "businessType": "epmpics",
            "jsonData": {
            "templateid": "pneumonia",
            "token": token
        },
            "method": "getUpDataInfoDetail"
    }      
    response = requests.post(sign_url, json=post_json).json()
    data = json.loads(response['data'])
    info_dict = {
            "add":data['add'],
            "areaStr": data['areaStr'],
            "updatainfo": [{"propertyname": i["propertyname"], "value": i["value"]} for i in
                            data['cusTemplateRelations']]
        }
    #随机温度
    a=random.uniform(36.2,36.8)
    temperature = round(a, 1)
    for i in info_dict['updatainfo']: 
        if i['propertyname'] == 'temperature':
            i['value'] = temperature
    #校外打卡提交json
    check_json = {
    "businessType": "epmpics",
    "method": "submitUpInfo",
    "jsonData": {
        "add": info_dict['add'],
        "areaStr": info_dict['areaStr'],
        "cardNo": "null",
        "customerid": userInfo['customerId'],
        "deptStr": {
            "deptid": userInfo['classId'],
            "text": userInfo['classDescription'],
        },
        "phonenum": ownPhone,
        "stuNo": userInfo['stuNo'],
        "templateid": "pneumonia",
        "upTime": "null",
        "userid": userInfo['userId'],
        "username": userInfo['username'],
        "deptid": userInfo['classId'],
        "updatainfo": info_dict['updatainfo'],
        "source": "app",
        "reportdate": round(time.time()),
        "gpsType": 1,
        "token": token
    }
}
    res = requests.post(sign_url, json=check_json) 
    return res

#微信通知
def wechatPush(title,sckey,success,fail,result):    
    strTime = getNowTime()
    page = json.dumps(result.json(), sort_keys=True, indent=4, separators=(',', ': '),ensure_ascii=False)
    content = f"""
`{strTime}` 
#### 打卡成功用户：
`{success}` 
#### 打卡失败用户:
`{fail}`
#### 主用户打卡信息:
```
{page}
```
### 😀[收藏此项目](https://github.com/YooKing/HAUT_autoCheck)

        """
    data = {
            "text":title,
            "desp":content
    }
    scurl='https://sc.ftqq.com/'+sckey+'.send'
    try:
        req = requests.post(scurl,data = data)
        if req.json()["errmsg"] == 'success':
            print("Server酱推送服务成功")
        else:
            print("Server酱推送服务失败")
    except:
        print("微信推送参数错误")

if __name__ == '__main__':
    mark = 1
    main()

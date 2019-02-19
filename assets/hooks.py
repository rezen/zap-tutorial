import time
import re
from os.path import expanduser
import sys
from pip._internal import main as pip
import requests
import os

# http://localhost:3000/api-docs/
print("-- Loading hooks scripts ...")

# Adding packages to a new Docker image is better, but this works as POC
pip(['install', "-I", "-q", "--user", "selenium", "beautifulsoup4"])
home = expanduser("~")
sys.path.append(home + "/.local/lib/python2.7/site-packages/")
print("-- Finished adding extras")

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver import FirefoxOptions

def do_scan(zap, target):
  print("-- Starting active scan of %s" % target)
  scan_id = zap.ascan.scan(target, recurse=False)
  time.sleep(5)

  while(int(zap.ascan.status(scan_id)) < 100):
    print('-- Active Scan progress %: ' + zap.ascan.status(scan_id))
    time.sleep(5)
  print('-- Active Scan complete')


def do_login(zap, driver, target):
  driver.get(target)
  time.sleep(2)
  user = os.environ.get("TEST_USER", "test@test.com")
  passwd = os.environ.get("TEST_PASS", "testtest")

  print("-- Login with browser")
  try:
    driver.find_element_by_css_selector("#userEmail").send_keys(user)
    driver.find_element_by_css_selector("#userPassword").send_keys(passwd)
    driver.find_element_by_css_selector("#loginButton").click()
  except:
    pass
  
  time.sleep(1)
  crawl_angular(zap, target, driver)  

def get_firefox(zap):
  driver_bin = zap.selenium.option_firefox_driver_path
  proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': zap._ZAPv2__proxies['http'],
    'ftpProxy': zap._ZAPv2__proxies['http'],
    'sslProxy': zap._ZAPv2__proxies['http'],
    'noProxy': ''
  })
  profile = webdriver.FirefoxProfile()
  profile.accept_untrusted_certs = True
  opts = FirefoxOptions()
  opts.add_argument("--headless")

  driver = webdriver.Firefox(proxy=proxy, executable_path=driver_bin, firefox_options=opts, firefox_profile=profile)
  return driver


def crawl_angular(zap, target, driver=None):
  if driver is None:
    driver = get_firefox(zap)
    driver.get(target)

  whens = _find_ng_whens(zap)
  print("-- Crawling angular routes (%s)" % len(whens))

  for endpoint in whens:
    if 'logout' in endpoint or 'logoff' in endpoint:
      continue

    print("-- Navigating angular endpoint /#%s" % endpoint)
    try:
      driver.get(target + '/#' + endpoint)
      # Taking a screenshot
      # time.sleep(1)
      # idx = whens.index(endpoint)
      # driver.save_screenshot('/zap/wrk/screen-%s.png' % idx)
    except:
      pass

def _extract_when_endpoints(body):
  findings = re.findall(r"\.when\([^)]+\)", body)
  endpoints = []
  for match in findings:
    parts = match.split('"')
    if len(parts) < 2:
      continue
    endpoints.append(match.split('"')[1])
  return endpoints


def _find_ng_whens(zap):
  time.sleep(1)
  messages = zap.search.messages_by_response_regex('\.when\(["\']')
  unique_endpoints = set()
  for msg in messages:
    full_msg = zap.core.message(msg["id"])
    body = full_msg['responseBody']
    for endpoint in _extract_when_endpoints(body):
      unique_endpoints.add(endpoint)
  return list(unique_endpoints)


def _list_scanners(zap, policy='Default Policy'):
  all_scanners = zap.ascan.scanners(scanpolicyname=policy)
  disabled_scanners = [s for s in all_scanners if s['enabled'] != 'true']
  enabled_scanners = [s for s in all_scanners if s['enabled'] == 'true']

  print("-- Scanners disabled (%s)" %  len(disabled_scanners))
  for scanner in disabled_scanners:
    print('   x [' + scanner['id'] + '] ' + scanner['name'])

  print("-- Scanners enabled (%s)" % len(enabled_scanners))
  for scanner in enabled_scanners:
    print('   + [' + scanner['id'] + '] ' + scanner['name'] + ' | ' + scanner['attackStrength'])


def start_zap(port, extra_zap_params):
  return port, extra_zap_params + [
    '-addoninstall', 'ascanrulesAlpha', 
    '-addoninstall', 'ascanrulesBeta',
    '-addoninstall', 'sqliplugin',
    '-addoninstall', 'domxss',
  ]


def zap_started(zap, target):  
  print("-- ZAP started!")
  ignore = [
    ".*node_modules.*",
    "%s/public.*" % target,
    "%s/i18n.*" % target,
    "%s/css.*" % target,
  ]

  print("-- Ignore scanning private " + zap.ascan.exclude_from_scan("%s/private.*" % target))  
  print("-- Ignore scanning dist " + zap.ascan.exclude_from_scan("%s/dist.*" % target))  
  print("-- Ignore scanning ftp " + zap.ascan.exclude_from_scan("%s/ftp.*" % target))
  print("-- Ignore scanning socket.io " + zap.ascan.exclude_from_scan("%s/socket.io.*" % target))

  for endpoint in ignore:
    print(("-- Ignore spider %s " % endpoint) +  zap.spider.exclude_from_scan(endpoint))
    print(("-- Ignore scanning %s " % endpoint) + zap.ascan.exclude_from_scan(endpoint))


def zap_spider(zap, target):
  username = os.environ.get("TEST_USER", "test@test.com")
  passwd = os.environ.get("TEST_PASS", "testtest")
  # Register
  payload = {
    "email": username,
    "password": passwd,
    "passwordRepeat": passwd,
    "securityQuestion": {
      "id": 1,
      "question": "Your eldest siblings middle name?",
      "createdAt": "2018-11-07T21:19:32.395Z",
      "updatedAt": "2018-11-07T21:19:32.395Z"
    },
    "securityAnswer": passwd
  }

  try:
    requests.post("%s/api/Users/" % target, proxies=zap._ZAPv2__proxies, verify=False, json=payload)
    print("-- Creating user")
  except Error as err:
    print(err)

  # POST to the login endpoint so spider/scans have another node to attack
  res = requests.post(target + '/rest/user/login', proxies=zap._ZAPv2__proxies, verify=False, json={
    "email": username,
    "password": passwd,
  })
  print("-- API Login Response " + res.text)
  print("-- Setting spider duration " +  zap.spider.set_option_max_duration("1"))

  return zap, target


def zap_ajax_spider(zap, target, max_time):
  # The regular spider already ran ... if we don't clear exclusions
  # the page won't load the css/js needed to render everything
  zap.spider.clear_excluded_from_scan()
  zap.spider.set_option_max_duration("1")
  zap.ajaxSpider.set_option_max_duration("1")

  # Use selenium to login to the app and crawl real quick
  driver = get_firefox(zap)
  do_login(zap, driver, target)
  
  print("-- Trying XSS ...")
  try:
    driver.get(target + '#/search?q=<script>alert("XSS")</script>')
    time.sleep(1)
    alert = driver.switch_to.alert
    alert.accept()

    driver.get(target + '#/track-result?id=<script>alert("XSS")</script>')
    time.sleep(1)
    alert = driver.switch_to.alert
    alert.accept()
  except:
    pass
  
  driver.quit()
  return zap, target + '/#/search?q=example', 1

def zap_active_scan(zap, target, policy):
  # zap.ascan.disable_all_scanners()
  # zap.ascan.enable_scanners([], scanpolicyname=policy)
  print(zap.ascan.policies(scanpolicyname=policy))
  skippable_scanners = list(set([
    '41', '43', '0', '7', '90020', '40032',
    '10029', '10032', '10035', '10040', '10045', '10046', 
    '10047', '10049', '10050', '10051', '10052', '2011', '2',
    '3192', '10053', '10056', '10057', '10058', '10061', '10095',
    '64', '10094','90034', '10096', '10097', '10099', '10104', 
    '10105', '10107', '20014', '20015', '20016', '2012', '1823', 
    '20017', '2012', '1823', '20018', '20019', '30001', '30002', 
    '30003', '40008', '40009', '40013', '40015', '40020', '40021', 
    '40022', '40023', '40025', '40027', '6', '60100', '40003', '42',
    '60101', '90021', '90023', '90024', '90025', '90026', '90027', 
    '90028', '90029', '90030', '90033','40028', '40029', '20012', '40019'
  ]))
  print("-- Skipping scanners " + zap.ascan.disable_scanners(','.join(skippable_scanners), scanpolicyname=policy))

  sql_scanners = ['40024', '40018', '90018']

  for id in sql_scanners:
    print(("-- Upping attack strength for id=%s " % id) + zap.ascan.set_scanner_attack_strength(id, "HIGH", policy))
  
  # do_scan(zap, target + '/rest/user/login')

  for id in sql_scanners:
    print(("-- Setting normal attack strength for id=%s " % id) + zap.ascan.set_scanner_attack_strength(id, "DEFAULT", policy))

  # High strength DOM XSS
  # scanner_dom_xss = "40026"  
  # print("-- Upping DOM XSS strength " + zap.ascan.set_scanner_attack_strength(scanner_dom_xss, "HIGH", policy))
  
  # Time box individual scans to a time limit
  # zap.ascan.set_option_max_rule_duration_in_mins("1")
  
  # Time box the entire active scan
  zap.ascan.set_option_max_scan_duration_in_mins("10")

  _list_scanners(zap)

  # Increase the amount of threads if local target
  if "172." in target or "127." in target or "192." in target:
    new_threads = "12"
    was_threads = zap.ascan.option_thread_per_host
    up_threads = zap.ascan.set_option_thread_per_host(new_threads)
    print("-- Upping threads per host from " + was_threads + " to " + new_threads + " " +  up_threads)

  return zap, target, policy


def zap_pre_shutdown(zap):
  print("-- Found urls ")
  # print(zap.search.  zap.search.urls_by_url_regex('.*api.*'))
  for endpoint in zap.core.urls():
    print("  - %s" % endpoint)
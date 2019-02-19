import time
import re
from os.path import expanduser
import sys
from pip._internal import main as pip
import requests
import os

print("-- Loading hooks scripts ...")

# Adding packages to a new Docker image is better, but this works as POC
pip(['install', "-I", "-q", "--user", "selenium", "beautifulsoup4"])
home = expanduser("~")
sys.path.append(home + "/.local/lib/python2.7/site-packages/")
print("-- Finished adding extras")

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver import FirefoxOptions

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
  zap.spider.exclude_from_scan("TODO")


def zap_access_target(zap, target):
  return zap, target


def zap_spider(zap, target):
  username = os.environ.get("TEST_USER", "test@test.com")
  passwd = os.environ.get("TEST_PASS", "testtest")
  return zap, target


def zap_ajax_spider(zap, target, max_time):
  return zap, target, 1


def zap_active_scan(zap, target, policy):
  return zap, target, policy


def zap_pre_shutdown(zap):
    pass
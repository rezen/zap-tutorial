import sys
import time
from zapv2 import ZAPv2

if len(sys.argv) > 1:
    target = sys.argv[1]
else: 
    target = "http://localhost:3000"

print("Spidering target %s" % target)

zap = ZAPv2()

zap.spider.exclude_from_scan(".*node_modules.*")
zap.spider.exclude_from_scan("%s/public.*" % target)
zap.spider.exclude_from_scan("%s/i18n.*" % target)

scan_id = zap.spider.scan(url=target, maxchildren=2, recurse=True, contextname=None, subtreeonly=None)

time.sleep(2)

while (int(zap.spider.status(scan_id)) < 100):
  print("Spider progress " + zap.spider.status(scan_id) + "%")
  time.sleep(2)

print("Spider scan completed")
zap.spider.clear_excluded_from_scan()
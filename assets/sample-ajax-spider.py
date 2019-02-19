import sys
import time
from zapv2 import ZAPv2

if len(sys.argv) > 1:
    target = sys.argv[1]
else: 
    target = "http://localhost:3000/#/"

print("AJAX Spidering target %s" % target)

zap = ZAPv2()
print(zap.ajaxSpider.option_browser_id)
print(zap.ajaxSpider.set_option_browser_id("chrome"))
zap.ajaxSpider.set_option_max_duration("1")
print(zap.ajaxSpider.scan(target))

while (zap.ajaxSpider.status == 'running'):
    print('Ajax Spider running, found urls: ' + zap.ajaxSpider.number_of_results)
    time.sleep(5)

print("AJAX spider scan completed "  + zap.ajaxSpider.status )
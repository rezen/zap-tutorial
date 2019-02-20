import sys
import time
from zapv2 import ZAPv2

if len(sys.argv) > 1:
    target = sys.argv[1]
else: 
    target = "http://localhost:3000/#/"

print("-- AJAX Spidering target %s" % target)

zap = ZAPv2()
print("-- Checking browser option (%s)" % zap.ajaxSpider.option_browser_id)
print("-- Setting browser to chrome " +  zap.ajaxSpider.set_option_browser_id("chrome"))

zap.ajaxSpider.set_option_max_duration("1")
print("-- Starting AJAX Spider "  + zap.ajaxSpider.scan(target))

try:
    while (zap.ajaxSpider.status == 'running'):
        sys.stdout.write("\r   ... urls found (%s)" % zap.ajaxSpider.number_of_results)
        sys.stdout.flush()
        time.sleep(1)
except KeyboardInterrupt:
    zap.ajaxSpider.stop(scan_id)

print("")
print("-- AJAX spider scan completed "  + zap.ajaxSpider.status )
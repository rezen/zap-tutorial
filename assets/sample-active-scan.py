import sys
import time
from zapv2 import ZAPv2

if len(sys.argv) > 1:
    target = sys.argv[1]
else: 
    target = "http://localhost:3000"

print("-- Running active scan against %s" % target)

zap = ZAPv2()
print("-- Ignore node_modules " + zap.ascan.exclude_from_scan("%s/node_modules.*" % target))
print("-- Ignore scanning private " + zap.ascan.exclude_from_scan("%s/private.*" % target)) 
print("-- Ignore scanning dist " + zap.ascan.exclude_from_scan("%s/dist.*" % target))
print("-- Ignore scanning css " + zap.ascan.exclude_from_scan("%s/css.*" % target))
print("-- Ignore scanning ftp " + zap.ascan.exclude_from_scan("%s/ftp.*" % target))
print("-- Ignore scanning socket.io " + zap.ascan.exclude_from_scan("%s/socket.io.*" % target))

zap.urlopen(target)
policy = "Default Policy"
scan_id = zap.ascan.scan(target, recurse=True, scanpolicyname=policy)

time.sleep(2)

try:
    while(int(zap.ascan.status(scan_id)) < 100):
        print('-- Active Scan progress %: ' + zap.ascan.status(scan_id))
        time.sleep(1)
except KeyboardInterrupt:
    zap.ascan.stop(scan_id)

print('-- Active Scan complete')

scan_target, details = zap.ascan.scan_progress(scan_id)
for plugin in details.get('HostProcess', []):
    name, id, quality, status, x, reqs, found = plugin['Plugin']
    found = int(found)
    if found > 0:
        print("  - Found [%s] %s (found %s)" % (id, name, found))
zap.ascan.clear_excluded_from_scan()
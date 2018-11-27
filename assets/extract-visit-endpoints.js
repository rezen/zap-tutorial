function logger() {
    print('[' + this['zap.script.name'] + '] ' + arguments[0]);
  }
  
  var Control           = Java.type('org.parosproxy.paros.control.Control')
  var ExtensionSelenium = Java.type('org.zaproxy.zap.extension.selenium.ExtensionSelenium');
  var Thread            = Java.type('java.lang.Thread');
  var WebDriver         = Java.type('org.openqa.selenium.WebDriver');
  
  function getAll(re, body) {
    var match;
    var matches = []; 
    do {
      match = re.exec(body);
      if (match) {
          matches.push(match);
      }
    } while (match);
    return matches;
  }
  
  function invokeWith(msg) {
    var selenium = Control.getSingleton().getExtensionLoader().getExtension(ExtensionSelenium.class);
    var driver   = selenium.getWebDriverProxyingViaZAP(1, 'firefox');
    var url = msg.getRequestHeader().getURI();
    var root = url.getScheme() + '://' + url.getHost();
    if (url.getPort() != 80 && url.getPort() != 443) {
      root += ':' + url.getPort();
    }
    var body = msg.getResponseBody().toString();
    // For capturing angular.js router urls
    var regexWhen = /\.when\(["']([^"']+)["']/g;
    // For capturing angular.js AJAX requests
    var regexGet = /\.get\(["']([^"']+)["']/g;
  
    var matches = getAll(regexWhen, body);
    var links = []
  
    for (var i in matches) {
      var link = root + '/#' +  matches[i][1];
      if (links.indexOf(link) !== -1) {
        continue;
      }
      links.push(link);
    }
       
    matches = getAll(regexGet, body);
  
    for (var i in matches) {
      var link = root +  matches[i][1];
      if (links.indexOf(link) !== -1) {
        continue;
      }
      links.push(link);
    }
  
    for (var i in links) {
      driver.get(links[i]);
      Thread.sleep(1000);
    }
  
    driver.quit();
  }
# zap-tutorial

## Goals
- Learn about some ZAP Basics
  - Interface overview
  - Launching browser proxying through ZAP
  - Contexts
  - Spidering
  - Authentication
  - Active Scanning
  - Alerts
- Learn about ZAP's script engine
  - Creating a custom `httpsender` script
  - Creating a `standalone` script which uses selinium to automate some browser interactions
- Learn about baseline scans
  - Automate security scans against Juice Shop
  - Customize the baseline scan using hooks

The goal of this excersize is go use the ZAP GUI to setup the basic configurations needed to run an authenticated scan.
We'll touch on some gotchas with the scans and use the ZAP hooks to configure and enhance the scans. Throughout 
this tutorial we will be assumming you are running Juice Shop in docker `localhost:3000` but if not, substitute the URL
with your url.

## Requirements
- docker
- OWASP ZAP (Weekly build)

## Preparation
You will need need to a running instance of [OWASP Juice Shop](https://github.com/bkimminich/juice-shop). I recommend running
it locally using Docker!

`docker run --rm -p 3000:3000 bkimminich/juice-shop`

## Getting Started
### Firing up ZAP
If you are using Windows or Mac you can use the ZAP icon to get it started. If you are using linux, `zap.sh` should be in your 
PATH, so you can call that to start things up. You can also run the ZAP GUI through Docker, but the instructions for that are not 
includeds.

### Set up Browser
*Optional*  
Once you have ZAP started you can start proxying the browser traffic through it. You'll need install an addon/extension
or change some settings in your browser. ZAP includes profiles to start a browser with the correct settings (which I recommend using)

#### Chrome
You can use an extension configure chrome on the fly to set the Proxy
https://chrome.google.com/webstore/detail/proxy-switcher-and-manage/onnfghpihccifgojkpnnncpagjcdbjod?hl=en


## Configuring Contexts

In ZAP, there the configuration of context, whhich ZAP uses are used to group together a set of urls. In the case of Juice Shop, there is really only one url to configure, but other applications may have endpoints with different hostnames that use the 
same underlying application that could be grouped together with a Context.

### Adding a URL
At minium, a context needs to have a URL, to get things started let's add the application root url. The easiest way to do this is
to focus in the ZAP window and Launch Browser in the Quick Start window.

In the browser that ZAP just started, visit `http://localhost:3000/`, once the page loads, go back to the ZAP application. 
Near the bottom of ZAP, there will be a number of tabs, (History, Search, Alerts, Output), click on the History tab and confirm 
you can see requests being tracked. After that, in the left sidebar of ZAP, under **Sites** you will see a set of url trees generated from the traffic. Right click (or control click) the url root `http://localhost:3000/` and in the context menu that 
popped up `Include in Context > Default Context`. It will bring up the context editor and you will see it added `http://localhost:3000.*`


### Spidering
Now that we have the context setup, let's go ahead and test the spider out. Let's go ahead and configure the max time to be 1 minute, we don't want this to run forever, just a quick scan. You'll see it found some additional static assets but nothing terribly helpful. Since this is a single page application, there isn't much content generated server side for the spider to crawl. Most of the application interface is generated client side by angularjs.  In this case we could easily use a quick bash script to achieve similar affects.

```sh
T=http://localhost:3000/; curl -x 127.0.0.1:8080 "${T}" | grep 'src' | cut -d '"' -f 2 | xargs -I{} curl  -x 127.0.0.1:8080 -sIXGET "${T}{}"
T=http://localhost:3000/; curl -x 127.0.0.1:8080 "${T}" | grep 'href' | cut -d '"' -f 2 | xargs -I{} curl -x 127.0.0.1:8080 -sIXGET "${T}{}"
```

So the question becomes, how do you crawl applications that are primarily rendered client side? Luckily ZAP has an extenion to address this, the AJAX Spider!

#### AJAX Spider
To kick off the AJAX Spider, let's go back to the **Sites** tab and then right click on the request labeled `http://localhost:3000`. 
In the menu that popped up click Attack > AJAX Spider. This will prompt a dialog to appear with which you can configure the scan. Select 
the context. Start with selecting Firefox as the browser, then check the option **Show Advanced Options** and another tab **Options** will appear in the dialog. 
Go ahead and set *Number of Browser Windows to Open* to 2 and set *Maximum Duration* to 5. Now go ahead and click *Start Scan* to kicks things off.
In the bottom portion of ZAP, you will see a scrolling list being updated with new requests being tracked from the browser. If you switch to 
the browser that started you can see ZAP interacting with the application. It doesn't get everything but you can observe many more new requests 
have been discovered. In the **Sites** tab if you drill down into some of the urls such as `rest`, you will notice all these pages have a red spider icon 
next to them, indicating they were found by the AJAX Spider.


### Adding Authentication
The application has a portion of functionality that is available only to logged in users. To fully test out your application, you need
to also test out the logic as a logged in user. ZAP has several means to authenticate to your application and keep track of authenication
state. To start things out with testing out doing an authenticated scans, let's go ahead and add a registered user. 

#### Register User
Browse to `http://localhost:3000/#/register` & register a new user. For the purpose of this tutorial, use the following
information.

- *Email* input `test@test.com`
- *Password* input `testtest`
- *Security Question* 
  - Select `Your eldest siblings middle name`
  - Input `test`

#### Login
With the information you just registered with, browse to the login url `http://localhost:3000/#/login`. When you login
the request will be added to the **History** in ZAP. Search for the POST that included the login information, you should
find a POST request to `http://localhost:3000/rest/user/login`. Right click (or control click) that request in the history
and in the context menu that prompted click, Right click (or control click) `Flag as Context > Default Context : JSON-based Auth Login Request` (if you only see the option for `Form-based`... that means your version of ZAP is out of date). The will bring up the Context Authentication editor settings.  You will notice the post data with 
the authentication information as well as a couple parameters for selecting Username & Password. Go ahead and set the username and password parameters to the correspending JSON
attributes.

Exit the context editor and go back to the request, you will notice in the response headers there is no set cookie. In the response body you will
find the response data. 

```
{"authentication":{"token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0dXMiOiJzdWNjZXNzIiwiZGF0YSI6eyJpZCI6OSwiZW1haWwiOiJ0ZXN0QHRlc3QuY29tIiwicGFzc3dvcmQiOiIwNWE2NzFjNjZhZWZlYTEyNGNjMDhiNzZlYTZkMzBiYiIsImNyZWF0ZWRBdCI6IjIwMTgtMTAtMjkgMjI6MjM6MDIuODQwICswMDowMCIsInVwZGF0ZWRBdCI6IjIwMTgtMTAtMjkgMjI6MjM6MDIuODQwICswMDowMCJ9LCJpYXQiOjE1NDA4NTE5ODksImV4cCI6MTU0MDg2OTk4OX0.Xw-5Kz4PPgAus2Pij1SsQl7dbUfufP8i_KN2So1MQyI5TCh9u1BdDrpmpyccxM6JAp5YWPgESJj6mjInr5lsGAOcIJyH_paBb9f3o5KO2KyLdzFrYWd7fMWfCNeQeGBakUcNTU0JnzUl8QxZBTbfIYG4QOPWaPlSJo5rEN5lB1o","bid":4,"umail":"test@test.com"}}
```
 

The request that follows is `GET http://localhost:3000/rest/user/whoami` which you will notice has a header called `Authorization` which uses the token from the response body of the login request. In body if the response, you should see some info about your user.`{"user":{"id":9,"email":"test@test.com"}}`.  If you visit that url directly, with your browser, the content of the page is `{"user":{}}` - the Authorization header is not added to request and there is not authenticated.

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0dXMiOiJzdWNjZXNzIiwiZGF0YSI6eyJpZCI6OSwiZW1haWwiOiJ0ZXN0QHRlc3QuY29tIiwicGFzc3dvcmQiOiIwNWE2NzFjNjZhZWZlYTEyNGNjMDhiNzZlYTZkMzBiYiIsImNyZWF0ZWRBdCI6IjIwMTgtMTAtMjkgMjI6MjM6MDIuODQwICswMDowMCIsInVwZGF0ZWRBdCI6IjIwMTgtMTAtMjkgMjI6MjM6MDIuODQwICswMDowMCJ9LCJpYXQiOjE1NDA4NTE5ODksImV4cCI6MTU0MDg2OTk4OX0.Xw-5Kz4PPgAus2Pij1SsQl7dbUfufP8i_KN2So1MQyI5TCh9u1BdDrpmpyccxM6JAp5YWPgESJj6mjInr5lsGAOcIJyH_paBb9f3o5KO2KyLdzFrYWd7fMWfCNeQeGBakUcNTU0JnzUl8QxZBTbfIYG4QOPWaPlSJo5rEN5lB1o
```

This request is initiated as a client side AJAX request using a spec called [JWT](https://jwt.io/). Currently ZAP doesn't have a notion of the `Authorization` header for 
sessions so this is where ZAPs scripting engine will come into play! With ZAP's scripting engine, we can easily 
add to or augment it's functionality.

##### Adding JavaScript Support
Out of the box, ZAP doesn't support JavaScript as a scripting engine, so you need to add it.
ZAP has an *Add-on Marketplace* where we can add support for additioanl scripting engines.
 There is an icon with a red blue green & blue box stacked, if you click that it will bring up
 the marketplace modal. After it pops up, switch to the *Marketplace* tab and search for the `Script Console` and install it. 

 Now in the left sidebar next to the **Sites** click **+** to add **Scripts**. This will bring
 into focus in the sidebar. Drill into Scripting > Scripts > HTTP Sender. Then right click 
 on the *HTTP Sender* and with that context menu click *New Script*. Name the script `maintain-jwt.js`  & set the Script Engine to *ECMAScript* (do no check the box that says enable).

```js
if (typeof println == 'undefined') this.println = print;

// Logging with the script name is super helpful!
function logger() {
  print('[' + this['zap.script.name'] + '] ' + arguments[0]);
}

// Control.getSingleton().getExtensionLoader().getExtension(ExtensionUserManagement.class);
var HttpSender = Java.type('org.parosproxy.paros.network.HttpSender');
var ScriptVars = Java.type('org.zaproxy.zap.extension.script.ScriptVars');
var HtmlParameter = Java.type('org.parosproxy.paros.network.HtmlParameter')
var COOKIE_TYPE   = org.parosproxy.paros.network.HtmlParameter.Type.cookie;

function sendingRequest(msg, initiator, helper) {  
  if (initiator === HttpSender.AUTHENTICATION_INITIATOR) {
    logger("Trying to auth")
	return msg;
  }

  var token = ScriptVars.getGlobalVar("jwt-token")
  if (!token) {return;}
  var headers = msg.getRequestHeader();
  var cookie = new HtmlParameter(COOKIE_TYPE, "token", token);
  msg.getRequestHeader().getCookieParams().add(cookie);
  // For all non-authentication requests we want to include the authorization header
  logger("Added authorization token " + token.slice(0, 20) + " ... ")
  msg.getRequestHeader().setHeader('Authorization', 'Bearer ' + token);
  return msg;
}

function responseReceived(msg, initiator, helper) {
  var resbody     = msg.getResponseBody().toString()
  var resheaders  = msg.getResponseHeader()

  if (initiator !== HttpSender.AUTHENTICATION_INITIATOR) {
     var token = ScriptVars.getGlobalVar("jwt-token");
     if (!token) {return;}

     var headers = msg.getRequestHeader();
     var cookies = headers.getCookieParams();
     var cookie = new HtmlParameter(COOKIE_TYPE, "token", token);
       
     if (cookies.contains(cookie)) {return;}
     msg.getResponseHeader().setHeader('Set-Cookie', 'token=' + token + '; Path=/;');
	return;
  }

  logger("Handling auth response")
  if (resheaders.getStatusCode() > 299) {
    logger("Auth failed")
    return;
  } 

  // Is response JSON? @todo check content-type
  if (resbody[0] !== '{') {return;}
  try {
    var data = JSON.parse(resbody);
  } catch (e) {
    return;
  }
  
  // If auth request was not succesful move on
  if (!data['authentication']) {return;}
	
  // @todo abstract away to be configureable
  var token = data["authentication"]["token"]
  logger("Capturing token for JWT\n" + token)
  ScriptVars.setGlobalVar("jwt-token", token)
  msg.getResponseHeader().setHeader('Set-Cookie', 'token=' + token + '; Path=/;');
}

```
(Another time we'll cover just the scripting aspect of ZAP)

Now that we have that script setup, let's test it out! Go ahead and visit the login page `http://localhost:3000/#/login` with the browser launched with ZAP and use your test account to login. After you login, back in ZAP in the **Script Console** tab you should see a message that says.

```
[maintain-jwt.js] Capturing token for JWT eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0dXMiOi
....
```
Now visit `http://localhost:3000/rest/user/whoami` directly in the browser and you will see you get JSON data with the 
user `{"user":{"id":9,"email":"test@test.com"}}`! Back in the **Script Console** you will see the script went ahead and added the header!

```
[maintain-jwt.js] Added authorization token eyJhbGciOiJSUzI1NiIs ... 
```

#### Authenticated Spidering
Now that we have a script forcing ensuring we have the right headers & cookies for authentication, let's go ahead and try spidering the application again!
So let's use the same setting we used earlier from the AJAX Spider [Settings](#AJAX Spider). Once the scan starts, check out the browser running the scan - you'll 
notice the user is logged in! (Logout & Your Basket links visible). Now the AJAX Spider will pick up some new paths that it couldn't find before!


### Scoreboard
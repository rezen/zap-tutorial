### Adding Authentication
The application has a portion of functionality that is available only to logged in users. To fully test out your application, you need
to also test out the logic as a logged in user. Some applications have features exposed without authenitcation, so it's 
very important to understand how to perform authenciated scans.
 ZAP has several means to authenticate to your application and keep track of authenication
state. To start things out with testing out doing an authenticated scans, let's go ahead and add a registered user. 

#### Register User
Let's go ahead and get first test user registered and setup to test authentication. Browse to 
`http://localhost:3000/#/register` & register a new user. For the purpose of this tutorial, use the following
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

```json
{
  "authentication": {
    "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0dXMiOiJzdWNjZXNzIiwiZGF0YSI6eyJpZCI6OSwiZW1haWwiOiJ0ZXN0QHRlc3QuY29tIiwicGFzc3dvcmQiOiIwNWE2NzFjNjZhZWZlYTEyNGNjMDhiNzZlYTZkMzBiYiIsImNyZWF0ZWRBdCI6IjIwMTgtMTAtMjkgMjI6MjM6MDIuODQwICswMDowMCIsInVwZGF0ZWRBdCI6IjIwMTgtMTAtMjkgMjI6MjM6MDIuODQwICswMDowMCJ9LCJpYXQiOjE1NDA4NTE5ODksImV4cCI6MTU0MDg2OTk4OX0.Xw-5Kz4PPgAus2Pij1SsQl7dbUfufP8i_KN2So1MQyI5TCh9u1BdDrpmpyccxM6JAp5YWPgESJj6mjInr5lsGAOcIJyH_paBb9f3o5KO2KyLdzFrYWd7fMWfCNeQeGBakUcNTU0JnzUl8QxZBTbfIYG4QOPWaPlSJo5rEN5lB1o",
    "bid": 4,
    "umail": "test@test.com"
  }
}
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
// Logging with the script name is super helpful!
function logger() {
  print('[' + this['zap.script.name'] + '] ' + arguments[0]);
}

// Control.getSingleton().getExtensionLoader().getExtension(ExtensionUserManagement.class);
var HttpSender    = Java.type('org.parosproxy.paros.network.HttpSender');
var ScriptVars    = Java.type('org.zaproxy.zap.extension.script.ScriptVars');
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


# Intro
Embedding security testing into your development lifecycle is more important than ever. Security issues present
liabilities to organizations that can grow bigger over time and are harder to address the later in the development
lifecycle they are discovered. How do you ensure you didn't expose `.git` directory? Are you using the right [security 
headers](https://securityheaders.com/) and settings?  Checking these things manually is error prone, so you really need to
this automatically. You also should do some basic sanity checks for the OWASP top 10. Luckily ZAP can handle all 
these kinds of checks for you!

ZAP has 3 different scanning scripts to test your application with different levels of depth they dig into
their application. We fill be focusing on the `zap-full-scan.py` to test against Juice Shop but be sure to 
check out all the options.

- zap-baseline.py
- zap-full-scan.py	
- zap-api-scan.py	

## Goals
The primary goal of this post is to script up scanning your application with ZAP. You will learn the methods for customizing
the  `zap-full-scan.py` which you can then apply to your application! Through the journey towards our goal, we  will touch on 
some additional topics necessary to reach our goal. 

- Learn about some ZAP Basics
  - Interface overview
  - Launching browser proxying through ZAP
  - Contexts
  - Spidering
  - Authentication
  - Active Scanning
  - Alerts
  - Fuzzing
- Learn about ZAP's script engine
  - Creating a custom `httpsender` script
  - Creating a `standalone` script which uses selinium to automate some browser interactions
- Learn about baseline scans
  - Automate security scans against Juice Shop
  - Customize the baseline scan using hooks

The end goal of this exercise is go use the ZAP GUI to setup the basic configurations needed to run an authenticated scan.
We'll touch on some gotchas with the scans and use the ZAP hooks to configure and enhance the scans. Throughout 
this tutorial we will be assuming you are running Juice Shop in docker `localhost:3000` but if not, substitute the URL
with your url.

**Links**
[ZAP Wiki Introduction](https://github.com/zaproxy/zaproxy/wiki/Introduction)
[ZAP Wiki Videos](https://github.com/zaproxy/zaproxy/wiki/Videos)
[Pluralsight Lesson](https://www.pluralsight.com/courses/owasp-zap-web-app-pentesting-getting-started)
# Preparation

## Requirements
If you want follow along you'll need the 
- Awareness of [OWASP Top 10](https://www.owasp.org/index.php/OWASP_Top_Ten_Cheat_Sheet#OWASP_Top_Ten_Cheat_Sheet)
- OWASP ZAP (Weekly build)
- Juice Shop web app
- docker
- curl
- jq
- python
- selenium

### Installing ZAP
Getting ZAP installed is pretty straight forward, download the appropriate [installer](https://github.com/zaproxy/zaproxy/wiki/Downloads) for your OS and install!

- [Youtube - Linux Install ](https://www.youtube.com/watch?v=MpuFW_mkJ3M)
- [Windows - Chocolately Package](https://chocolatey.org/packages/zap)

### Juice Shop
You will need need to a running instance of [OWASP Juice Shop](https://github.com/bkimminich/juice-shop). I recommend running
it locally using Docker! For the purpose of this tutorial, it will be running in docker with all relevant commands assuming 
that is the situation.

`docker run --net=host --rm -p 3000:3000 bkimminich/juice-shop`

### Firing up ZAP
If you are using Windows or Mac you can use the ZAP icon to get it started. If you are using linux, `zap.sh` should be in your 
PATH, so you can call that to start things up. You can also run the ZAP GUI through Docker, but the instructions for that are not 
included.

### Set up Browser
*Optional*  
Once you have ZAP started you can start proxying the browser traffic through it. You'll need install an addon/extension
or change some settings in your browser. ZAP includes profiles to start a browser with the correct settings (which I recommend using)

#### Chrome
You can use an extension configure chrome on the fly to set the Proxy
https://chrome.google.com/webstore/detail/proxy-switcher-and-manage/onnfghpihccifgojkpnnncpagjcdbjod?hl=en
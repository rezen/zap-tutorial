# Putting the Pieces Together

We've gone through different aspects of ZAP's functionality, tuning & configuring everything to
improve the quality of the scans for Juice Shop. Now the question is, how do we put all those 
pieces together, so we can run the `zap-full-scan.py` fully customized with everything we've worked on?


### Exporting Context
![Export Context](assets/images/zap-export-context.gif)

## Exportingc URLs
![Export Context](assets/images/zap-export-urls.gif)


```sh
time docker run --rm -v $(pwd):/zap/wrk/:rw \
    -t owasp/zap2docker-weekly zap-full-scan.py \
    -d -a -j \
    -t http://172.17.0.2:3000  \
    --hook=/zap/wrk/hooks.py
```
import json
import urllib2
from bs4 import BeautifulSoup
from flask import Flask
from flask import request
import requests
from PIL import Image
import pytesseract
import cv2
import os
import re
from autocorrect import spell
app = Flask(__name__)
@app.route('/getlinks')
def getvids():
    textToSearch = request.args.get('concept')
    query = urllib2.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html,"html5lib")
    arr=[]
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        if (not vid['href'].startswith("https://www.googleadservices.com")) and (not vid['href'].startswith("channel/")):
            arr.append( vid['href'].split("=")[-1])
            if (len(arr)==4):
                break
    dix= {"id1":arr[0],"id2":arr[1],"id3":arr[2],"id4":arr[3]}
    js=json.dumps(dix)
    return js

#@app.route('/concepts')
def keyConcepts(text):
    subscription_key = "8280c00a78e9487782155b5021417894"
    assert subscription_key

    text_analytics_base_url = "https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.0/"
    key_phrase_api_url = text_analytics_base_url + "keyPhrases"
    documents = {'documents' : [
      {'id': '1', 'language': 'en', 'text':text}
      ]}
    headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
    response  = requests.post(key_phrase_api_url , headers=headers, json=documents)
    resp = response.json()
    print resp
    keywords = resp["documents"]
    arr=keywords[0]["keyPhrases"][:10]

    ret_arr=[]
    for i in arr:
                 ret_arr.append({"concept":i})

    js = json.dumps(ret_arr)
    return js

@app.route('/getconcepts')
def ocr():
    #image=img
    image = cv2.imread('tesseract-test4.jpg')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    text = pytesseract.image_to_string(Image.open(filename), lang='eng')
    os.remove(filename)
    l = re.findall(r"[\w']+", text)
    l_cor = []
    flagger=[]
    text_cor=""
    for i in l:
        l_cor.append(spell(i))
        flagger.append(0)
        if i!=spell(i):
            flagger[-1]=1
    cur=''
    ctr=0 
    for i in text:
        if i.lower() not in "abcdefghijklmnopqrstuvwxyz":
            if cur.lower().isalpha():
                text_cor+=l_cor[ctr]
                ctr+=1
                cur=""
            text_cor=text_cor+i
        else:
            cur+=i
    return keyConcepts(text_cor)

#ocr()
if __name__=='__main__':
    app.debug=True
    app.run(host="0.0.0.0",port=5000)

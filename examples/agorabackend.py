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
from binascii import a2b_base64
from flask_cors import CORS,cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/getlinks')
@cross_origin()
def getvids():
    textToSearch = request.args.get('concept')
    print textToSearch
    query = urllib2.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html,"html5lib")
    arr=[]
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        if (not vid['href'].startswith("https://www.googleadservices.com")) and (not vid['href'].startswith("channel/") and vid['href'].find('channel/')==-1):
            arr.append( vid['href'].split("=")[-1])
            if (len(arr)==4):
                break
    d={}
    d["i1"]=arr[0]
    d["i2"]=arr[1]
    d["i3"]=arr[2]
    d["i4"]=arr[3]
    js=json.dumps(d)
    print js
    return js

#@app.route('/concepts')
def keyConcepts(text):
    subscription_key = "3ca06abc3220453e91c3cb580cb71e5f"
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
    if len(keywords[0]["keyPhrases"])>10:
        arr=keywords[0]["keyPhrases"][:10]
    else:
        arr=keywords[0]["keyPhrases"]

    ret_arr=[]
    for i in arr:
                 ret_arr.append({"concept":i})

    js = json.dumps(ret_arr)
    return js

@app.route('/getconcepts')
@cross_origin()
def ocr():
    #image=img
    #image = cv2.imread('tesseract-test4.jpg')
    image = cv2.imread('upload.png')
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
    '''
    print text
    print "-------------------------"
    print text_cor
    '''
    if text_cor.strip()=="":
        #text_cor="There is nothing here"
        return json.dumps([])
    #print text_cor+"%%%%%%%%%%%%%%%%%%%%%%%%"
    return keyConcepts(text_cor)

@app.route('/postimage',methods = ['POST'])
@cross_origin()
def decode_img():
    data = request.data
    ind =  data.find("base64,")
    binary_data = a2b_base64(data[ind+7:])
    
    fd = open('upload.png', 'wb')
    fd.write(binary_data)
    fd.close()
    return "200"

#ocr()
#'''
if __name__=='__main__':
    app.debug=True
    app.run(host="0.0.0.0",port=5000)
#'''

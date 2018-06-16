import requests
import json
from bs4 import BeautifulSoup
import re

def create_query(phrase):
    query_inc = re.sub("[']",'',phrase)
    query=re.sub(" ","+",query_inc)
    return query

def find_prod(prod="grey jacket for men"):
    response={}
    arr=[]
    fin_arr=[]
    query=create_query(prod)
    page = requests.get("https://www.flipkart.com/search?q="+query+"&marketplace=FLIPKART&otracker=start&as-show=on&as=off")
    soup = BeautifulSoup(page.content, 'html.parser')
    prodsrc = soup.find_all(class_="_2cLu-l")
    price=soup.find_all(class_="_1vC4OE")
    ctr=0
    arr=[]
    for i in prodsrc:
        arr.append("https://www.flipkart.com"+str(i['href']))
        ctr+=1
        if ctr>=4:
            break;
    ctr=0
    fin_arr.append(arr)
    arr=[]
    for i in price:
        arr.append("Rs "+str(i.get_text()[1:]))
        ctr+=1
        if ctr>=4:
            break;
    ctr=0
    fin_arr.append(arr)
    arr=[]
    response[prod]=fin_arr
    return response

print find_prod()
            


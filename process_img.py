import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from time import sleep
from tqdm import tqdm
import urllib.parse as ul
from os.path import basename
import os
import ast
import psutil
import threading
import pygame, time
from pygame.locals import *

df_links=[]

def soupify(url: str): # returns html of given webpage
    import requests
    from bs4 import BeautifulSoup

    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    
    return soup

def linkify(url: str):
    global progress
    soup = soupify(url)
    images = {}
    for image in soup.find_all('a'):
        if image.get('m') == None:
            pass
        else:
            try:
                images[re.sub(r'[^A-Za-z0-9 ]'," ",ast.literal_eval(image['m'])['t'])]=[
                    ast.literal_eval(image['m'])['purl'].replace(' ','%20').strip('"'),
                    ast.literal_eval(image['m'])['murl'].replace(' ','%20').strip('"')
                    ]
                progress[3]+=1
            except Exception as e: print(e)
    return images

def imagify(keys: list, variables, n):
    for key in keys:
        global progress
        global df_links
        links = linkify('https://www.bing.com/images/search?q='+str(key))
        df_links.append([key,links])
        parent = os.getcwd()+'\\'
        directory = re.sub(r'[^A-Za-z0-9 ]'," ",key)
        try:
            os.mkdir(parent+directory)
        except Exception as e: print(e)
        for link in links:
            try:
                r = requests.get(links[link][1])
                if 'image' in r.headers['Content-Type']:
                    print(link+': '+str(r))
                    data = r.content 
                    temp = open(parent+directory+'\\'+re.sub(r'[^A-Za-z0-9 ]',"",link)+'.jpg','wb')
                    temp.write(data)
                    temp.close()
                    progress[2]+=1
                else:
                    continue
            except Exception as e: print(e)
        progress[0]+=1
        #print('\n')

def pandas_fix(result):
    df={}
    for i, x in enumerate(df_links):
        titles=[]
        web_links=[]
        image_links=[]
        fluff=[]
        for j in df_links[i][1]:
            temp={}
            web_links.append('=HYPERLINK("'+df_links[i][1][j][0]+'","'+j+'")')
            image_links.append('=IMAGE("'+df_links[i][1][j][1]+'")')
        temp={'Links': web_links, 'Images': image_links}
        for w in range(0,100-len(temp['Links'])):
            fluff.append(None)
        for k in temp:
            df[str(df_links[i][0])+'_'+k]=temp[k]+fluff
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        display(pd.DataFrame(df))
    return pd.DataFrame(df)
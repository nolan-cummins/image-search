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
#from process_img import soupify, linkify, imagify, pandas_fix
import threading
import pygame, time
from pygame.locals import *

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

def prog():
    global progress
    global finish
    global to_print
    global file

    # Example file showing a basic pygame "game loop"
    
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((1000, 200))
    clock = pygame.time.Clock()
    pygame.display.set_caption('Bing')
    running = True
    print("Starting game")
    to_print=''
    font = pygame.font.SysFont('Arial', 40)
    file=''
    objects = []
    
    class Button():
            def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onePress=False):
                self.x = x
                self.y = y
                self.width = width
                self.height = height
                self.onclickFunction = onclickFunction
                self.onePress = onePress
                self.alreadyPressed = False
        
                self.fillColors = {
                    'normal': '#ffffff',
                    'hover': '#666666',
                    'pressed': '#333333',
                }
                
                self.buttonSurface = pygame.Surface((self.width, self.height))
                self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        
                self.buttonSurf = font.render(buttonText, True, (20, 20, 20))
        
                objects.append(self)
        
            def process(self):
                mousePos = pygame.mouse.get_pos()
                self.buttonSurface.fill(self.fillColors['normal'])
                if self.buttonRect.collidepoint(mousePos):
                    self.buttonSurface.fill(self.fillColors['hover'])
                    if pygame.mouse.get_pressed(num_buttons=3)[0]:
                        self.buttonSurface.fill(self.fillColors['pressed'])
                        if self.onePress:
                            self.onclickFunction()
                        elif not self.alreadyPressed:
                            self.onclickFunction()
                            self.alreadyPressed = True
                    else:
                        self.alreadyPressed = False
        
                self.buttonSurface.blit(self.buttonSurf, [
                    self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
                    self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
                ])
                screen.blit(self.buttonSurface, self.buttonRect)
        
    def button_proc():
        print('Button press')
        global file
        global progress
        global df_links
        df_links=[]
        #threaded_dict={}
        threads=psutil.cpu_count()-1
        thread={}
        t_num=['t1','t2','t3','t4','t5','t6','t7','t8']
        finish=True
        try:
            if file != '':
                print(file)
                lst = list(pd.read_csv(file, header=None)[0])
                chunks = np.array_split(lst, threads)
                progress=[0,len(lst),0,0]
                for i in range(0, threads):
                        thread[t_num[i]]=threading.Thread(target=imagify, args=(chunks[i], 0, i+1))
                for i in range(0, threads):
                    thread[t_num[i]].start()
                    print('Thread:'+t_num[i]+' starting. . .')
                for i in range(0, threads):
                    thread[t_num[i]].join()  
                while finish:
                    sleep(0.1)
                    to_print = 'Items: '+str(progress[0])+'/'+str(progress[1])+'     Images: '+str(progress[2])+'/'+str(progress[3])
                    print(to_print,end='\r')
                finish=False
                print('\n---- Processes Terminated\n')
        except Exception as e: 
            to_print=e
            print(e)

    Button(425, 130, 125, 50, 'Process', button_proc)
    
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            try:
                if event.type == pygame.QUIT:
                    running = False
                #print(event)
                #pygame.time.delay(100)
                if event.type == pygame.DROPFILE:
                    to_print = re.sub(r"\\",'/',event.file)
                    file = event.file
            except Exception as e: print(e)
                
    
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")
    
        # RENDER YOUR GAME HERE
        keys = pygame.key.get_pressed()
        try:
            if keys[pygame.K_q]:
                pygame.QUIT
                print("Closing game")
                running = False
            
            my_font = pygame.font.SysFont('Arial', 25)
            text_surface = my_font.render(str(to_print), False, (0, 0, 0))
            screen.blit(text_surface, (0,0))
    
            if to_print != '':   
                for object in objects:
                    #print(object)
                    object.process()
                    
        except Exception as e: print(e)
        # flip() the display to put your work on screen
        pygame.display.flip()
        clock.tick(60)  # limits FPS to 60
        
    pygame.quit()

print('Pygame starting')
progress_t = threading.Thread(target=prog)
progress_t.start()
progress_t.join()
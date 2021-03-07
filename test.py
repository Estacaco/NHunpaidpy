import nicehash
import time
import urllib, json
import requests
import logging
import tkinter as tk
import threading
from tkinter import *
from PIL import Image, ImageTk
from PIL import ImageOps
from PIL import ImageFont
from PIL import ImageDraw
import currency
import yaml
import currency
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import decimal
configfile = "config.yaml"

root=tk.Tk()

frame=tk.Frame(root,width=480,height=320)


# tk.Frame(root,width=480,height=320).pack() this makes a new frame over the one configured above
frame.configure(bg="blue")
frame.pack()
frame2=tk.Frame(root,width=100,height=100)
frame3=tk.Frame(root,width=100,height=100)
frame4=tk.Frame(root,width=100,height=100)
def currencystringtolist(currstring):
    # Takes the string for currencies in the config.yaml file and turns it into a list
    curr_list = currstring.split(",")
    curr_list = [x.strip(' ') for x in curr_list]
    return curr_list
def currencycycle(curr_list):
    # Rotate the array of currencies from config.... [a b c] becomes [b c a]
    curr_list = curr_list[1:]+curr_list[:1]
    return curr_list
def getData(config,whichcoin,other):
    geckourl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=cad&ids="+whichcoin
    rawlivecoin = requests.get(geckourl).json()
    logging.info(rawlivecoin[0])   
    liveprice = rawlivecoin[0]
    pricenow= float(liveprice['current_price'])
    alltimehigh = float(liveprice['ath'])
    other['volume'] = float(liveprice['total_volume'])
    logging.info("Getting Data")
    days_ago=int(config['ticker']['sparklinedays'])   
    endtime = int(time.time())
    starttime = endtime - 60*60*24*days_ago
    starttimeseconds = starttime
    endtimeseconds = endtime  
    geckourlhistorical = "https://api.coingecko.com/api/v3/coins/"+whichcoin+"/market_chart/range?vs_currency=cad&from="+str(starttimeseconds)+"&to="+str(endtimeseconds)
    print("got geckourlhistorical")
    rawtimeseries = requests.get(geckourlhistorical).json()
    print("Got price for the last "+str(days_ago)+" days from CoinGecko")
    timeseriesarray = rawtimeseries['prices']
    timeseriesstack = []
    length=len (timeseriesarray)
    i=0
    while i < length:
        timeseriesstack.append(float (timeseriesarray[i][1]))
        i+=1

    timeseriesstack.append(pricenow)
    if pricenow>alltimehigh:
        other['ATH']=True
    else:
        other['ATH']=False
    return timeseriesstack, other

def makeSpark(pricestack):
    # Draw and save the sparkline that represents historical data

    # Subtract the mean from the sparkline to make the mean appear on the plot (it's really the x axis)    
    x = pricestack-np.mean(pricestack)

    fig, ax = plt.subplots(1,1,figsize=(10,3))
    plt.plot(x, color='k', linewidth=6)
    plt.plot(len(x)-1, x[-1], color='r', marker='o')

    # Remove the Y axis
    for k,v in ax.spines.items():
        v.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axhline(c='k', linewidth=4, linestyle=(0, (5, 2, 1, 2)))

    # Save the resulting bmp file to the images directory
    plt.savefig("images/spark.png", dpi=40)
    imgspk = Image.open("images/spark.png")
    file_out = "images/spark.bmp"
    imgspk.save(file_out) 
    plt.clf() # Close plot to prevent memory error
    ax.cla() # Close axis to prevent memory error
    plt.close(fig) # Close plot

def Draw(config,pricestack,whichcoin,other):
    crypto_list = currencystringtolist(config['ticker']['currency'])
    crypto_list = currencycycle(crypto_list)
    whichcoin = crypto_list[0]
    host = 'https://api2.nicehash.com'
    organisation_id = '6802cbfc-7854-4ecb-8526-f6abb1439bb6'
    key = '3d13168f-6b85-44aa-bff5-20fb60731031'
    secret = '1f6a6143-5cd5-47a9-bf16-1d256d2dc9097d2ece65-ae84-4206-8138-23bbe8d5e4a4'
    private_api = nicehash.private_api(host, organisation_id, key, secret)
    accounts = private_api.get_accounts()
    accountsdata = str(accounts['total'])
    currencydata = str(accounts['currencies'])
    currencylist = currencydata.split(":")
    accountslist = accountsdata.split("'")
    wallet = float(accountslist[7]) #isolate total balance
    rate = float('{:.8}'.format(currencylist[7]))
    wallet = float(accountslist[7])
    total = wallet*rate
    balance = float('{:.2f}'.format(total))
    final = str(balance)

    unpaid = private_api.get_unpaid() #get unpaid json

    strdata = str(unpaid['data']) #grab "data" section and convert to string
    listdata = strdata.split(",") #organize
    maybe = float(listdata[2]) #grab total unpaid
    almost = format(float(maybe), '.8f') #convert form scientific to decimal float
    working = decimal.Decimal(almost) #convert from float to decimal
    ok = working * 100000000 #make whole number
    unpfd = int(ok) #convert to integer to drop decimals
    unpf = str(unpfd)
    geckourl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=cad&ids="+whichcoin
    rawlivecoin = requests.get(geckourl).json()
    logging.info(rawlivecoin[0])   
    liveprice = rawlivecoin[0]
    pricenow= float(liveprice['current_price'])
    pricenow = str(pricenow)
    output = tk.StringVar()
    output.set('$'+pricenow+'/'+whichcoin)
    load = Image.open("images/currency/"+whichcoin+".bmp")
    render = ImageTk.PhotoImage(load)
    img = Label(image=render)
    img.image = render
    img.place(x=40, y=20)

    load2 = Image.open("images/spark.bmp")
    render2 = ImageTk.PhotoImage(load2)
    img = Label(image=render2)
    img.image = render2
    img.place(x=40, y=150)

    frame2.place(x=40,y=122)


    text=Label(frame2,textvariable=output, fg='green', font=('helvetica', 12, 'bold'))
    text.pack()

    frame3.place(x=145,y=20)
    tbal = tk.StringVar()
    tbal.set('NiceHash Wallet Balance: $'+final)

    tbal2=Label(frame3,textvariable=tbal, fg='green', font=('helvetica', 12, 'bold'))
    tbal2.pack()

    frame4.place(x=145,y=40)
    unpv = tk.StringVar()
    unpv.set('NiceHash unpaid mining: '+unpf+' Sat')

    upt=Label(frame4,textvariable=unpv, fg='green', font=('helvetica', 12, 'bold'))
    upt.pack()
    print ('writing config')
def Refresher():

    other={}
    with open(configfile) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config['display']['orientation']=int(config['display']['orientation'])
    crypto_list = currencystringtolist(config['ticker']['currency'])
    fiat_list=currencystringtolist(config['ticker']['fiatcurrency'])
    mdisplay_list=currencystringtolist(config['mining']['display'])
    crypto_list = currencycycle(crypto_list)
    CURRENCY=crypto_list[0]
    FIAT=fiat_list[0]
    MDISPLAY=mdisplay_list[0]
    pricestack, ATH = getData(config,CURRENCY, other)
    config['ticker']['currency']=",".join(crypto_list)
    config['ticker']['fiatcurrency']=",".join(fiat_list)
    config['mining']['display']=",".join(mdisplay_list)
    with open(configfile, 'w') as f:
        data = yaml.dump(config, f)

    makeSpark(pricestack)
    for widget in frame2.winfo_children():
        widget.destroy()
    for widget in frame3.winfo_children():
        widget.destroy()
    for widget in frame4.winfo_children():
        widget.destroy()
#    frame.pack_forget()
    print ('refreshing')
    getData(config,CURRENCY,other)
    threading.Timer(10, Refresher).start()
    Draw(config, pricestack, CURRENCY, other)





Refresher()
root.mainloop()

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 22:36:42 2021

@author: rohit kumar
"""

#------------------------------------------------------------------------------------------------------------------------
#------------------import the required libraries 
#------------------------------------------------------------------------------------------------------------------------
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date


pd.set_option('display.max_columns', None)
sns.set(rc={'figure.figsize':(14,8)})

stock_df = pd.read_csv("f_o_stock_list.csv")
df = pd.DataFrame(columns = ["Date", "Symbol", "Open", "High", "Low", "Close"])

class my_dictionary(dict): 
  
    # __init__ function 
    def __init__(self): 
        self = dict() 
          
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value 
  
# Main Function 
plot_data_dict = my_dictionary() 
net_return = 0
symbol = []
position = []
entry = []
target = []
stop_loss = []
exit_price = []
last_close = []
pct_p_n_l  = []
target_limit = 2
stop_loss_limit = 0.5

for i in range(len(stock_df.symbol)):
    stock_data = yf.Ticker(str(stock_df.symbol[i]+".NS"))
    hist = stock_data.history(period="1d", interval="5m").reset_index()
    open_price = hist["Close"][3]
    close_price = hist["Close"].values[-3]
    if hist["Open"][0]>=max(hist["High"][0:4]):
        symbol.append(stock_df.symbol[i])
        position.append("Short")
        entry_price = hist["Open"][4]
        entry.append(entry_price)
        target.append(round((1-target_limit/100)*entry_price,1))
        stop_loss.append(round((1+stop_loss_limit/100)*entry_price,1))
        
        stock_data = yf.Ticker(str(stock_df.symbol[i]+".NS"))
        df = stock_data.history(period="1d", interval="1m").reset_index()[16:362]
        
        if df[(df["Open"] > round((1+stop_loss_limit/100)*entry_price,1)) | (df["Open"] < round((1-target_limit/100)*entry_price,1))]["Open"].empty:
            exit_price1 = df.Open[361]
            exit_price.append(exit_price1)
        else:
            exit_price1 = df[(df["Open"] > round((1+stop_loss_limit/100)*entry_price,1)) | (df["Open"] < round((1-target_limit/100)*entry_price,1))]["Open"].values[0]
            exit_price.append(exit_price1)
        last_close.append(hist["Close"].values[-1])
        p_n_l = round(100*(entry_price-exit_price1)/entry_price,2)
        plot_data_dict.add(stock_df.symbol[i], p_n_l)
        pct_p_n_l.append(p_n_l)
        net_return = net_return+p_n_l
        
    elif hist["Open"][0]<=min(hist["Low"][0:4]):
        symbol.append(stock_df.symbol[i])
        position.append("Long")
        entry_price = hist["Open"][4]
        entry.append(entry_price)
        target.append(round((1+target_limit/100)*entry_price,1))
        stop_loss.append(round((1-stop_loss_limit/100)*entry_price,1))
        
        stock_data = yf.Ticker(str(stock_df.symbol[i]+".NS"))
        df = stock_data.history(period="1d", interval="1m").reset_index()[16:362]
              
        if df[(df["Open"] > round((1+target_limit/100)*entry_price,1)) | (df["Open"] < round((1-stop_loss_limit/100)*entry_price,1))]["Open"].empty:
            exit_price1 = df.Open[361]
            exit_price.append(exit_price1)
        else:
            exit_price1 = df[(df["Open"] > round((1+target_limit/100)*entry_price,1)) | (df["Open"] < round((1-stop_loss_limit/100)*entry_price,1))]["Open"].values[0]
            exit_price.append(exit_price1)  
            
        last_close.append(hist["Close"].values[-1])
        p_n_l = round(100*(exit_price1-entry_price)/entry_price,2)
        plot_data_dict.add(stock_df.symbol[i], p_n_l)
        pct_p_n_l.append(p_n_l)
        net_return = net_return+p_n_l
    else:
        pass

print(symbol, position, entry, target, stop_loss, exit_price, last_close, pct_p_n_l)

data=dict(sorted(plot_data_dict.items(), key=lambda item: item[1]))
stock = list(data.keys())
change = list(data.values())
title = 'Strategy Intraday Return = ' + str(round(net_return,2))+' %'
sns.set_style('darkgrid')
ax0 = sns.barplot(x=stock, y=change)
ax0.set_xticklabels(ax0.get_xticklabels(), rotation=90, ha="right")
ax0.set_title(title)
plt.xlabel("Stock")
plt.ylabel("% Change")
plt.tight_layout()
plt.show()

canvas = canvas.Canvas("intraday_report_{}.pdf".format(date.today()), pagesize=letter)
canvas.setLineWidth(.3)
canvas.setFont('Helvetica', 9)


trader_record = ["Ashutosh", "Kumar", "15091992"]
fund_record = ["NA", "NA"]
    
canvas.line(6, 785, 605, 785)
canvas.line(6, 785, 6, 6)
canvas.line(605, 785, 605, 6)
canvas.line(6, 6, 605, 6)
canvas.drawString(260,760,"Open-High-Low Strategy")
canvas.drawString(480,750,"Date  :")
canvas.drawString(520,750,"{}".format(date.today()))
canvas.drawString(30,750,'Daily Intraday Trading Report')
canvas.drawString(30,735,'Client First Name : {}'.format(trader_record[0]))
canvas.drawString(30,720,'Client Last Name : {}'.format(trader_record[1]))
canvas.drawString(30,705,'Client ID : {}'.format(trader_record[2]))
          

opening_balance = fund_record[0]
closing_balance = fund_record[1]

canvas.drawString(430,720,'Opening Balance : {}'.format(opening_balance))
canvas.drawString(430,705,'Closing Balance :  {}'.format(closing_balance))
canvas.line(30, 700, 580, 700)
canvas.line(30, 698, 580, 698)
    
canvas.drawString(260,675,'Report Summary')
for i in range(3):
   canvas.line(30,  660-25*i, 580, 660-25*i)
for j in range(7):
   canvas.line(30+j*110,  610, 30+j*110,  660) 
          
canvas.drawString(40,642,"Total Traded Value")
canvas.drawString(155,642,"Trading Expense")
canvas.drawString(260,642,"Profit/Loss (MTM)")
canvas.drawString(380,642,"Net Profit/Loss")
canvas.drawString(500,642,"% Change")
          
          
total_traded_value=round(sum(entry)+sum(exit_price),2)
canvas.drawString(60,617,"{}".format(total_traded_value))
          
         
brokerage=round(0.001*total_traded_value,2)
canvas.drawString(175,617,"{}".format(brokerage))
          
         
p_n_l=round(sum(pct_p_n_l)*sum(entry)/100,2)
canvas.drawString(280,617,"{}".format(p_n_l))
          
canvas.drawString(390,617,"{}".format(round(p_n_l-brokerage,2)))
canvas.drawString(510,617,"{}".format(round(100*(p_n_l-brokerage)/sum(entry),2)))

          
canvas.drawString(30,585,'Trade Report')        

if len(symbol)>22:
    for k in range(23):
        canvas.line(30, 570-25*k, 580, 570-25*k)    
    for l in range(9):
        x=30+l*550/8
        canvas.line(x,  570, x,  570-(22)*25)
    
    canvas.drawString(40,553,"Symbol")  
    canvas.drawString(110,553,"Position")
    canvas.drawString(185,553,"Entry")
    canvas.drawString(250,553,"Target")
    canvas.drawString(315,553,"Stop Loss")
    canvas.drawString(400,553,"Exit")
    canvas.drawString(450,553,"Last Close")
    canvas.drawString(530,553,"% P/L")
    
    
    for r in range(21):
              canvas.drawString(35, 528-25*r,"{}".format(symbol[r]))
              canvas.drawString(120,528-25*r,"{}".format(position[r]))
              canvas.drawString(185,528-25*r,"{}".format(entry[r]))
              canvas.drawString(255,528-25*r,"{}".format(target[r]))
              canvas.drawString(325,528-25*r,"{}".format(stop_loss[r]))
              canvas.drawString(395,528-25*r,"{}".format(exit_price[r]))
              canvas.drawString(460,528-25*r,"{}".format(last_close[r]))
              canvas.drawString(535,528-25*r,"{}".format(pct_p_n_l[r]))

    canvas.showPage()
    
    canvas.setLineWidth(.3)
    canvas.setFont('Helvetica', 9)
          
    canvas.line(6, 785, 605, 785)
    canvas.line(6, 785, 6, 6)
    canvas.line(605, 785, 605, 6)
    canvas.line(6, 6, 605, 6)
    for k in range(len(symbol)-19):
        canvas.line(30, 770-25*k, 580, 770-25*k)    
    for l in range(9):
        x=30+l*550/8
        canvas.line(x,  770, x,  770-(len(symbol)-20)*25)
    canvas.drawString(45,753,"Symbol")  
    canvas.drawString(115,753,"Position")
    canvas.drawString(190,753,"Entry")
    canvas.drawString(255,753,"Target")
    canvas.drawString(320,753,"Stop Loss")
    canvas.drawString(400,753,"Exit")
    canvas.drawString(455,753,"Last Close")
    canvas.drawString(530,753,"% P/L")
    
    for r in range(len(symbol)-21):
              canvas.drawString(35, 728-25*r,"{}".format(symbol[21+r]))
              canvas.drawString(120,728-25*r,"{}".format(position[21+r]))
              canvas.drawString(185,728-25*r,"{}".format(entry[21+r]))
              canvas.drawString(255,728-25*r,"{}".format(target[21+r]))
              canvas.drawString(325,728-25*r,"{}".format(stop_loss[21+r]))
              canvas.drawString(395,728-25*r,"{}".format(exit_price[21+r]))
              canvas.drawString(460,728-25*r,"{}".format(last_close[21+r]))
              canvas.drawString(535,728-25*r,"{}".format(pct_p_n_l[21+r]))      
          
    canvas.save()

else:
    for k in range(len(symbol)+1):
       canvas.line(30, 570-25*k, 580, 570-25*k)    
    for l in range(9):
        x=30+l*550/8
        canvas.line(x,  570, x,  570-(len(symbol))*25)
    canvas.drawString(40,553,"Symbol")  
    canvas.drawString(110,553,"Position")
    canvas.drawString(185,553,"Entry")
    canvas.drawString(250,553,"Target")
    canvas.drawString(315,553,"Stop Loss")
    canvas.drawString(395,553,"Exit")
    canvas.drawString(450,553,"Last Close")
    canvas.drawString(530,553,"% P/L")



  
    
    
    

# -*- coding: utf-8 -*-
"""
Created on Sat May 16 19:23:03 2020

@author: Admin
"""



import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
from backtrader.feeds import GenericCSVData
import backtrader.indicators as btind
import pandas as pd
# Import the backtrader platform
import backtrader as bt
import calendar
import math
from backtrader import *
import numpy as np
# Create a Stratey





class TestStrategy(bt.Strategy):
    
    

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt1 = dt or self.datas[0].datetime.date(0)
        dt = dt or self.datas[0].datetime.time(0)
        print('%s %s, %s' % (dt1.isoformat(),dt.isoformat(), txt))    
        
        
       
        
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.datavol = self.datas[0].volume

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.trade_counter=0
        
        self.day_open=0
        self.buy_ind=0
        self.sell_ind=0
        
        self.ema_200 = btind.MovAv.EMA(self.dataclose, period=200)
        self.ema_26 = btind.MovAv.EMA(self.dataclose, period=26)
        self.ema_12 = btind.MovAv.EMA(self.dataclose, period=12)
        
        self.crossover = bt.ind.CrossOver(self.ema_12, self.ema_26)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):

        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        global period_high,sl_high,period_low,sl_low
        

        if self.order:
            return


        if not self.position:
            if self.ema_12[0] < self.ema_26[0] and self.ema_12[-1] > self.ema_26[-1] and self.dataclose[0] < self.ema_200[0] :
                self.sell(size = 0.1)
#                self.log('ema_200 , %.2f' % self.ema_200[0])
#                self.log('Close , %.2f' % self.dataclose[0])
#                self.log('ema_26 , %.2f' % self.ema_26[0])
#                self.log('ema_12 , %.2f' % self.ema_12[0])
                self.sell_ind= self.sell_ind +1
                period_high = self.datahigh.get(size=16)
                sl_high  = max(period_high)
                
                
                
            if self.ema_12[0] > self.ema_26[0] and self.ema_12[-1] < self.ema_26[-1] and self.dataclose[0] > self.ema_200[0] :
                self.buy(size = 0.1)
#                self.log('ema_200 , %.2f' % self.ema_200[0])
#                self.log('Close , %.2f' % self.dataclose[0])
#                self.log('ema_26 , %.2f' % self.ema_26[0])
#                self.log('ema_12 , %.2f' % self.ema_12[0])
                self.buy_ind= self.buy_ind +1
                period_low = self.datalow.get(size=16)
                sl_low  = max(period_low)
                
                        
        else:
#            if self.buy_ind > 0:
#                if self.dataclose[0] < sl_low and self.dataclose[-1] > sl_low:
#                    self.close()
#                    #self.log('SL HIT , %.2f' % sl_low)
            
            if self.buy_ind > 0:
                if self.dataclose[0]  < self.ema_26[0] and self.dataclose[-1]  > self.ema_26[-1]:
                        self.close()
                        self.buy_ind= self.buy_ind -1
                        #self.log('Tagret/sl hit , %.2f' %  self.ema_12[0])

            
#            if self.sell_ind > 0:
#                if self.dataclose[0] > sl_high and self.dataclose[-1] < sl_high:
#                    self.close()
#                    #self.log('SL HIT , %.2f' % sl_high)
                    
            if self.sell_ind > 0:
                if self.dataclose[0]  > self.ema_26[0] and self.dataclose[-1]  < self.ema_26[-1]:
                    self.close()
                    self.sell_ind= self.sell_ind -1
                    #self.log('Tagret/sl hit , %.2f' %  self.ema_12[0])

                        
                        
#        if self.position != 0:
#            if self.data.datetime.time() == datetime.time(15,5):
#                self.close()
#                #self.cancel(order)
                
def printDrawDownAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    drawdown = round(analyzer.drawdown, 2)
    moneydown = round(analyzer.moneydown, 2)
    length = analyzer.len
    max_dd = round(analyzer.max.drawdown, 2)
    max_md = round(analyzer.max.moneydown, 2)
    max_len = analyzer.max.len

    #Designate the rows
    h1 = ['Drawdown', 'Moneydown', 'Length']
    h2 = ['Max drawdown','Max moneydown', 'Max len']
    r1 = [drawdown, moneydown,length]
    r2 = [max_dd, max_md, max_len]
    #Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    #Print the rows
    print_list = [h1,r1,h2,r2]
    row_format ="{:<15}" * (header_length + 1)
    print("Drawdown Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))
        
        
def printTradeAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total,2)
    strike_rate = round((total_won / total_closed),2) * 100
    #Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate','Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    #Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    #Print the rows
    print_list = [h1,r1,h2,r2]
    row_format ="{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()



    # Add a strategy
    cerebro.addstrategy(TestStrategy)


    os.chdir(r'E:\Work\CRYPTO\datafolder')
    # Declare position of each column in csv file
    data = bt.feeds.GenericCSVData(dataname='btc_4h_2017-2020.csv',
    #                     dtformat=('%Y-%m-%d'),
    #                     tmformat=('%H:%M:%S'),
                         #dtformat=("%Y-%m-%d %H:%M:%S"),
                         dtformat=("%d-%m-%Y %H:%M"),
#                         sessionstart=datetime.time(9, 20),
#                         sessionend=datetime.time(15, 15),
                         timeframe=bt.TimeFrame.Minutes,
                         compression=1,                     
                         datetime=0,
                         high=1,
                         low=2,
                         open=3,
                         close=4,
                         volume=5,
                         openinterest=-1,
                         reverse= True,
                         #fromdate=date(2017,1,1),
                         #todate=datetime(2020,4,9)
                        )
    

    
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

 
    cerebro.broker.setcash(150.0)

    cerebro.broker.setcommission(commission=0.2,margin=10.0, mult=1.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())


    import backtrader.analyzers as btanalyzers

    cerebro.addanalyzer(btanalyzers.SQN, _name='SQN')

    #cerebro.addanalyzer(btanalyzers.DrawDown, _name='DrawDown')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(btanalyzers.Returns, _name='Returns')
    #cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='TradeAnalyzer')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='AnnualReturn')
    
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.004, annualize=True, _name='SharpeRatio')


    
    thestrats = cerebro.run()
    thestrat = thestrats[0]
#    
    #print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())

    print('SQN:', thestrat.analyzers.SQN.get_analysis())
    print('SharpeRatio:', thestrat.analyzers.SharpeRatio.get_analysis())
    print('TimeReturn:', thestrat.analyzers.AnnualReturn.get_analysis())
#    print('DrawDown:', thestrat.analyzers.DrawDown.get_analysis())
#    print('Returns:', thestrat.analyzers.Returns.get_analysis())
#    print('TradeAnalyzer:', thestrat.analyzers.TradeAnalyzer.get_analysis())

    printTradeAnalysis(thestrat.analyzers.ta.get_analysis())
    printDrawDownAnalysis(thestrat.analyzers.dd.get_analysis())

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


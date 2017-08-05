# WAVE RIDER V1.1
# A really sloppy trading bot designed for times of high volatility


import time
import sys
import datetime
from poloniex import poloniex

pair = "USDT_BTC" #the pair you are trading
padding = 5.0 #amount of padding in USDT in between the 24hr high and 24hr low. MUST BE A FLOAT.

#---------------Set these to the value of your last trade you made before you starting the bot. MUST BE A FLOAT.
lastBuyPrice = 0000.000000000 #set this to 0.0 if the last trade you made before starting the bot was a sell order
lastSellPrice = 2779.78100000 #set this to 0.0 if the last trade you made before starting the bot was a buy order
#---------------------------------------------------------------------------------------------------------------

money = .007 #the amount of money you are gambling with. MUST BE A FLOAT.
diff = 30.0 #The price change amount you want to wait for in between trades. MUST BE A FLOAT.

#These basically just buy or sell if 1 hour has elapsed since the last trade. Yes i know it's hacky.
#The whole idea here is to keep the bot trading at all times.
buyProtection = True
sellProtection = True

conn = poloniex('API-KEY-GOES-HERE','API-SECRET-GOES-HERE')

# DO NOT TOUCH ANYTHING BELOW THIS LINE!
price = 0.0 #DO NOT TOUCH
lastTradeTime = 0 #DO NOT TOUCH
averages = [] #DO NOT TOUCH
wAverage = 0.0 # DO NOT TOUCH
errcnt = 0 #DO NOT TOUCH
period = 300 #DO NOT TOUCH. The time in seconds the bot will requst info from the ticker.

if (lastBuyPrice > 0.0):
    lastOrder = 0
else:
    lastOrder = 1

while True:
    httpErr = False
    endTime = int(time.time())
    try:
        currentValues = conn.api_query("returnTicker")
    except Exception as e:
        httpErr = True
        errcnt = errcnt + 1
        print e
    currentPairPrice = currentValues[pair]["last"]
    hrHigh = currentValues[pair]["high24hr"]
    hrLow = currentValues[pair]["low24hr"]
    low = currentValues[pair]["lowestAsk"]
    high = currentValues[pair]["highestBid"]
    if (wAverage == 0.0):
        wAverage = float(currentPairPrice)
    if (httpErr is False):
        print "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now()) + " Average: %f Ask: %f Bid: %f Last: %f" % (wAverage,float(low),float(high),float(currentPairPrice))
    buyDiff = abs(lastBuyPrice - float(currentPairPrice))
    sellDiff = abs(lastSellPrice - float(currentPairPrice))
    if (lastBuyPrice < wAverage and lastBuyPrice < float(currentPairPrice) and buyDiff >= diff and lastOrder != 1 and float(currentPairPrice) > float(hrLow) + padding):
        try:
            price = float(currentPairPrice) + 1.0 #this is a workaround until i can figure out how to use postOnly option
            orderNumber = conn.sell(pair,price,money)
            print "----Order number----"
            print orderNumber["orderNumber"]
            print "--------------------"
        except Exception as e:
            if (e is 'error' or "'error'"):
                print e
                print 'Trade error. Trade aborted. Shutting down.'
                sys.exit(1)
        print 'SELL ORDER @ $%f' % price
        lastSellPrice = float(currentPairPrice)
        lastOrder = 1
        lastTradeTime = int(time.time())
    if (lastSellPrice > wAverage and lastSellPrice > float(currentPairPrice) and sellDiff >= diff and lastOrder != 0 and float(currentPairPrice) < float(hrHigh) - padding):
        try:
            price = float(currentPairPrice) - 1.0
            orderNumber = conn.buy(pair,price,money)
            print "----Order number----"
            print orderNumber["orderNumber"]
            print "--------------------"
        except Exception as e:
            if (e is 'error' or "'error'"):
                print e
                print 'Trade error. Trade aborted. Shutting down.'
                sys.exit(1)
        print 'BUY ORDER @ $%f' % price
        lastBuyPrice = float(currentPairPrice)
        lastOrder = 0
        lastTradeTime = int(time.time())
    if (abs(lastTradeTime - endTime) > 3600 and lastOrder != 0 and float(currentPairPrice) < float(hrHigh) and lastSellPrice > float(currentPairPrice) and buyProtection is True):
        try:
            print 'It has been more than 1 hour since the last trade.'
            print 'Placing a buy order to secure a new position'
            price = float(currentPairPrice) - 1.0
            orderNumber = conn.buy(pair,price,money)
            print "----Order number----"
            print orderNumber["orderNumber"]
            print "--------------------"
        except Exception as e:
            if (e is 'error' or "'error'"):
                print e
                print 'Trade error. Trade aborted. Shutting down.'
                sys.exit(1)
        print 'BUY ORDER @ $%f' % price
        lastBuyPrice = float(currentPairPrice)
        lastOrder = 0
        lastTradeTime = int(time.time())
    if (abs(lastTradeTime - endTime) > 3600 and lastOrder != 1 and float(currentPairPrice) > float(hrLow) and lastBuyPrice < float(currentPairPrice) and sellProtection is True):
        try:
            print 'It has been more than 1 hour since the last trade.'
            print 'Placing sell order to secure a new position'
            price = float(currentPairPrice) + 1.0
            orderNumber = conn.sell(pair,price,money)
            print "----Order number----"
            print orderNumber["orderNumber"]
            print "--------------------"
        except Exception as e:
            if (e is 'error' or "'error'"):
                print e
                print 'Trade error. Trade aborted. Shutting down.'
                sys.exit(1)
        print 'SELL ORDER @ $%f' % price
        lastSellPrice = float(currentPairPrice)
        lastOrder = 1
        lastTradeTime = int(time.time())
    if (httpErr is False):
        averages.append(float(currentPairPrice))
    if (len(averages) > 4):
        del averages[0]
    if (errcnt > 1):
        averages = []
        errcnt = 0
        print "Weighted average reset due to too many http errors."
    if (len(averages) > 0):
        wAverage = sum(averages) / len(averages)
    time.sleep(int(period))

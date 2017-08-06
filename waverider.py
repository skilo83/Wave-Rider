# WAVE RIDER V1.2
# A really sloppy trading bot designed for times of high volatility


import time
import sys
import datetime
import argparse
from poloniex import poloniex

parser = argparse.ArgumentParser(description='These arguments must entered by the user in this exact order.')
parser.add_argument('lastSellPrice', type=float, help='The last price you SOLD at before starting the bot or 0.0 if last order was a buy order.')
parser.add_argument('lastBuyPrice', type=float, help='The last price you BOUGHT at before starting the bot or 0.0 if the last order was a sell order.')
parser.add_argument('money', type=float, help='The amount of money you want to trade with')
parser.add_argument('diff', type=float, help='The amount you want to wait for the market to change in between trades.')
parser.add_argument('padding', type=float, help='The amount of padding between 24hrH and 24hrL. 5.0 - 10.0 recomended')
parser.add_argument('pair', type=str, help='The pair you are trading. USDT_BTC BTC_XMR etc.')
args = parser.parse_args()

pair = args.pair
padding = args.padding
lastBuyPrice = args.lastBuyPrice
lastSellPrice = args.lastSellPrice
money = args.money
diff = args.diff

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
lastTradeTime = int(time.time()) - 50

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

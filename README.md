# Wave Rider
A user configurable crypto currency trading bot for poloniex.

## Use at your own risk!
I am not responsible for any losses you may incur from the use of this script.

Requires python 3.x

Setup:

    copy and paste your api keys from poloniex into the included text files.

Usage:

    python3 waverider.py <lastsellprice> <lastbuyprice> <money> <diff> <padding> <pair>
    
Help:

    python3 waverider.py -h
    
"What in tarnation does all this mean?"

Last sell price:
    
    the price you last sold at before starting the bot. Set to 0.0 if last trade was a buy order.
    
Last buy price:

    the price you last bought at before starting the bot. Set to 0.0 if last trade was a sell order.
    
money:

    the amount of money you want to trade with
    
diff:

    the amount you want the market to change before making another trade
    
padding:

    an amount in between the 24hr high and 24hr low. can be set to 0.0 if you dont want it.
    
pair:

    the pair you are trading. USDT_BTC BTC_XMR etc etc.

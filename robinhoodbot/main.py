import robin_stocks as r
import pandas as pd
import numpy as np
import ta as ta
from pandas.plotting import register_matplotlib_converters
from ta import *
from misc import *
from tradingstats import *
from config import *

#Log in to Robinhood
#Put your username and password in a config.py file in the same directory (see sample file)
login = r.login(rh_username,rh_password)

#Safe divide by zero division function
def safe_division(n, d):
    return n / d if d else 0

def get_watchlist_symbols():
    """
    Returns: the symbol for each stock in your watchlist as a list of strings
    """
    my_list_names = []
    symbols = []
    for name in r.get_all_watchlists(info='name'):
        my_list_names.append(name)
    for name in my_list_names:
        list = r.get_watchlist_by_name(name)
        for item in list:
            instrument_data = r.get_instrument_by_url(item.get('instrument'))
            symbol = instrument_data['symbol']
            symbols.append(symbol)
    return symbols

def get_portfolio_symbols():
    """
    Returns: the symbol for each stock in your portfolio as a list of strings
    """
    symbols = []
    holdings_data = r.get_open_stock_positions()
    for item in holdings_data:
        if not item:
            continue
        instrument_data = r.get_instrument_by_url(item.get('instrument'))
        symbol = instrument_data['symbol']
        symbols.append(symbol)
    return symbols

def get_position_creation_date(symbol, holdings_data):
    """Returns the time at which we bought a certain stock in our portfolio

    Args:
        symbol(str): Symbol of the stock that we are trying to figure out when it was bought
        holdings_data(dict): dict returned by r.get_open_stock_positions()

    Returns:
        A string containing the date and time the stock was bought, or "Not found" otherwise
    """
    instrument = r.get_instruments_by_symbols(symbol)
    url = instrument[0].get('url')
    for dict in holdings_data:
        if(dict.get('instrument') == url):
            return dict.get('created_at')
    return "Not found"

def get_modified_holdings():
    """ Retrieves the same dictionary as r.build_holdings, but includes data about
        when the stock was purchased, which is useful for the read_trade_history() method
        in tradingstats.py

    Returns:
        the same dict from r.build_holdings, but with an extra key-value pair for each
        position you have, which is 'bought_at': (the time the stock was purchased)
    """
    holdings = r.build_holdings()
    holdings_data = r.get_open_stock_positions()
    for symbol, dict in holdings.items():
        bought_at = get_position_creation_date(symbol, holdings_data)
        bought_at = str(pd.to_datetime(bought_at))
        holdings[symbol].update({'bought_at': bought_at})
    return holdings

def get_last_crossing(df, days, symbol="", direction=""):
    """Searches for a crossing between two indicators for a given stock

    Args:
        df(pandas.core.frame.DataFrame): Pandas dataframe with columns containing the stock's prices, both indicators, and the dates
        days(int): Specifies the maximum number of days that the cross can occur by
        symbol(str): Symbol of the stock we're querying. Optional, used for printing purposes
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwaords cross. Optional, used for printing purposes

    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
    """
    prices = df.loc[:,"Price"]
    shortTerm = df.loc[:,"Indicator1"]
    LongTerm = df.loc[:,"Indicator2"]
    dates = df.loc[:,"Dates"]
    lastIndex = prices.size - 1
    index = lastIndex
    found = index
    recentDiff = (shortTerm.at[index] - LongTerm.at[index]) >= 0
    if((direction == "above" and not recentDiff) or (direction == "below" and recentDiff)):
        return 0
    index -= 1
    while(index >= 0 and found == lastIndex and not np.isnan(shortTerm.at[index]) and not np.isnan(LongTerm.at[index]) \
                        and ((pd.Timestamp("now", tz='UTC') - dates.at[index]) <= pd.Timedelta(str(days) + " days"))):
        if(recentDiff):
            if((shortTerm.at[index] - LongTerm.at[index]) < 0):
                found = index
        else:
            if((shortTerm.at[index] - LongTerm.at[index]) > 0):
                found = index
        index -= 1
    if(found != lastIndex):
        if((direction == "above" and recentDiff) or (direction == "below" and not recentDiff)):
            print(symbol + ": Short SMA crossed" + (" ABOVE " if recentDiff else " BELOW ") + "Long SMA at " + str(dates.at[found]) \
                +", which was " + str(pd.Timestamp("now", tz='UTC') - dates.at[found]) + " ago", ", price at cross: " + str(prices.at[found]) \
                + ", current price: " + str(prices.at[lastIndex]))
        return (1 if recentDiff else -1)
    else:
        return 0

def five_year_check(stockTicker):
    """Figure out if a stock has risen or been created within the last five years.

    Args:
        stockTicker(str): Symbol of the stock we're querying

    Returns:
        True if the stock's current price is higher than it was five years ago, or the stock IPO'd within the last five years
        False otherwise
    """
    instrument = r.get_instruments_by_symbols(stockTicker)
    list_date = instrument[0].get("list_date")
    if ((pd.Timestamp("now") - pd.to_datetime(list_date)) < pd.Timedelta("5 Y")):
        return True
    fiveyear = r.get_historicals(stockTicker,span='5year',bounds='regular')
    closingPrices = []
    for item in fiveyear:
        closingPrices.append(float(item['close_price']))
    recent_price = closingPrices[len(closingPrices) - 1]
    oldest_price = closingPrices[0]
    return (recent_price > oldest_price)

def golden_cross(stockTicker, n1, n2, days, direction=""):
    """Determine if a golden/death cross has occured for a specified stock in the last X trading days

    Args:
        stockTicker(str): Symbol of the stock we're querying
        n1(int): Specifies the short-term indicator as an X-day moving average.
        n2(int): Specifies the long-term indicator as an X-day moving average.
                 (n1 should be smaller than n2 to produce meaningful results, e.g n1=50, n2=200)
        days(int): Specifies the maximum number of days that the cross can occur by
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwaords cross. Optional, used for printing purposes

    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
        False if direction == "above" and five_year_check(stockTicker) returns False, meaning that we're considering whether to
            buy the stock but it hasn't risen overall in the last five years, suggesting it contains fundamental issues
    """
    if(direction == "above" and not five_year_check(stockTicker)):
        return False
    history = r.get_historicals(stockTicker,span='year',bounds='regular')
    closingPrices = []
    dates = []
    for item in history:
        closingPrices.append(float(item['close_price']))
        dates.append(item['begins_at'])
    price = pd.Series(closingPrices)
    dates = pd.Series(dates)
    dates = pd.to_datetime(dates)
    sma1 = ta.volatility.bollinger_mavg(price, n=int(n1), fillna=False)
    sma2 = ta.volatility.bollinger_mavg(price, n=int(n2), fillna=False)
    series = [price.rename("Price"), sma1.rename("Indicator1"), sma2.rename("Indicator2"), dates.rename("Dates")]
    df = pd.concat(series, axis=1)
    cross = get_last_crossing(df, days, symbol=stockTicker, direction=direction)
    if(cross) and plot:
        show_plot(price, sma1, sma2, dates, symbol=stockTicker, label1=str(n1)+" day SMA", label2=str(n2)+" day SMA")
    return cross

def sell_holdings(symbol, holdings_data):
    """ Place an order to sell all holdings of a stock.

    Args:
        symbol(str): Symbol of the stock we want to sell
        holdings_data(dict): dict obtained from get_modified_holdings() method
    """
    shares_owned = int(float(holdings_data[symbol].get("quantity")))
    if not debug:
        r.order_sell_market(symbol, shares_owned)
    print("####### Selling " + str(shares_owned) + " shares of " + symbol + " #######")

def buy_holdings(potential_buys, profile_data, holdings_data):
    """ Places orders to buy holdings of stocks. This method will try to order
        an appropriate amount of shares such that your holdings of the stock will
        roughly match the average for the rest of your portfoilio. If the share
        price is too high considering the rest of your holdings and the amount of
        buying power in your account, it will not order any shares.

    Args:
        potential_buys(list): List of strings, the strings are the symbols of stocks we want to buy
        symbol(str): Symbol of the stock we want to sell
        holdings_data(dict): dict obtained from r.build_holdings() or get_modified_holdings() method
    """
    cash = float(profile_data.get('cash'))
    portfolio_value = float(profile_data.get('equity')) - cash
    ideal_position_size = (safe_division(portfolio_value, len(holdings_data))+cash/len(potential_buys))/(2 * len(potential_buys))
    prices = r.get_latest_price(potential_buys)
    for i in range(0, len(potential_buys)):
        stock_price = float(prices[i])
        if(ideal_position_size < stock_price < ideal_position_size*1.5):
            num_shares = int(ideal_position_size*1.5/stock_price)
        elif (stock_price < ideal_position_size):
            num_shares = int(ideal_position_size/stock_price)
        else:
            print("####### Tried buying shares of " + potential_buys[i] + ", but not enough buying power to do so#######")
            break
        print("####### Buying " + str(num_shares) + " shares of " + potential_buys[i] + " #######")
        if not debug:
            r.order_buy_market(potential_buys[i], num_shares)

def scan_stocks():
    """ The main method. Sells stocks in your portfolio if their 50 day moving average crosses
        below the 200 day, and buys stocks in your watchlist if the opposite happens.

        ###############################################################################################
        WARNING: Comment out the sell_holdings and buy_holdings lines if you don't actually want to execute the trade.
        ###############################################################################################

        If you sell a stock, this updates tradehistory.txt with information about the position,
        how much you've earned/lost, etc.
    """
    if debug:
        print("----- DEBUG MODE -----\n")
    print("----- Starting scan... -----\n")
    register_matplotlib_converters()
    watchlist_symbols = get_watchlist_symbols()
    portfolio_symbols = get_portfolio_symbols()
    holdings_data = get_modified_holdings()
    potential_buys = []
    sells = []
    print("Current Portfolio: " + str(portfolio_symbols) + "\n")
    print("Current Watchlist: " + str(watchlist_symbols) + "\n")
    print("----- Scanning portfolio for stocks to sell -----\n")
    for symbol in portfolio_symbols:
        cross = golden_cross(symbol, n1=50, n2=200, days=30, direction="below")
        if(cross == -1):
            sell_holdings(symbol, holdings_data)
            sells.append(symbol)
    profile_data = r.build_user_profile()
    print("\n----- Scanning watchlist for stocks to buy -----\n")
    for symbol in watchlist_symbols:
        if(symbol not in portfolio_symbols):
            cross = golden_cross(symbol, n1=50, n2=200, days=10, direction="above")
            if(cross == 1):
                potential_buys.append(symbol)
    if(len(potential_buys) > 0):
        buy_holdings(potential_buys, profile_data, holdings_data)
    if(len(sells) > 0):
        update_trade_history(sells, holdings_data, "tradehistory.txt")
    print("----- Scan over -----\n")
    if debug:
        print("----- DEBUG MODE -----\n")

#execute the scan
scan_stocks()

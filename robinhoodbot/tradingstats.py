import robin_stocks as r
import pandas as pd
import json

def update_trade_history(symbols, holdings_data, file_name):
    """ Writes data about a trade to a JSON file, containing the sell date, buy date,
        price at which the stock was bought and sold at, etc.

    Args:
        symbols(list): List of strings, strings are the symbols of the stocks we've just sold and want to write data for.
        holdings_data(dict): dict obtained from get_modified_holdings() method. We need this method rather than r.build_holdings() to get a stock's buying date
        file_name(str): name of the file we are writing the data to. Should be "tradehistory.txt" if this method is normally called by scan_stocks().
                        If you want to write to another file, create a new text file with two empty brackets with an empty line between them, to meet JSON formatting standards.
    """
    with open(file_name) as json_file:
        data = json.load(json_file)
    current_time = str(pd.Timestamp("now"))
    data[current_time] = ({})
    for symbol in symbols:
        data[current_time].update({symbol: holdings_data[symbol]})
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

def read_trade_history(file_name):
    """ Reads data about previous trades from JSON file and prints it out

    Args:
        file_name(str): name of the file we are reading from. Should be "tradehistory.txt" by default
    """
    with open(file_name) as json_file:
        data = json.load(json_file)
    for sell_date, event in data.items():
        print(sell_date + ": ")
        for symbol, dict in event.items():
            quantity, price, change, percent, bought_at = str(int(float(dict.get("quantity")))), dict.get("price"), dict.get("equity_change"), dict.get("percent_change"), dict.get("bought_at")
            print("\tSold " + quantity + " shares of "+ symbol + " at " + price + ", " + change + " (" +
                percent + "%) profit/loss, bought on " + bought_at)

def get_total_gains_minus_dividends():
    """ Returns the amount of money you've gained/lost through trading since the creation of your account, minus dividends
    """
    profileData = r.load_portfolio_profile()
    print(profileData)
    allTransactions = r.get_bank_transfers()
    deposits = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'deposit')) # and (x['state'] == 'completed'))
    withdrawals = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'withdraw') and (x['state'] == 'completed'))
    money_invested = deposits - withdrawals
    print(deposits)
    dividends = r.get_total_dividends()
    percentDividend = dividends/money_invested*100
    totalGainMinusDividends =float(profileData['extended_hours_equity'])-dividends-money_invested
    return totalGainMinusDividends

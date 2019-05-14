import robin_stocks as r
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

def show_plot(price, firstIndicator, secondIndicator, dates, label1="", label2=""):
    """Displays a chart of the price and indicators for a stock

    Args:
        price(Pandas series): Series containing a stock's prices
        firstIndicator(Pandas series): Series containing a technical indicator, such as 50-day moving average
        secondIndicator(Pandas series): Series containing a technical indicator, such as 200-day moving average
        dates(Pandas series): Series containing the dates that correspond to the prices and indicators
        label1(str): Chart label of the first technical indicator
        label2(str): Chart label of the first technical indicator

    Returns:
        True if the stock's current price is higher than it was five years ago, or the stock IPO'd within the last five years
        False otherwise
    """
    plt.figure(figsize=(10,5))
    plt.title(symbol)
    plt.plot(dates, price, label="Closing prices")
    plt.plot(dates, firstIndicator, label=label1)
    plt.plot(dates, secondIndicator, label=label2)
    plt.yticks(np.arange(price.min(), price.max(), step=((price.max()-price.min())/15.0)))
    plt.legend()
    plt.show()

def get_equity_data():
    """Displays a pie chart of your portfolio holdings
    """
    holdings_data = r.build_holdings()
    equity_data = {}
    for key, value in holdings_data.items():
        equity_data[key] = {}
        equity_data[key][name] = value.get('name')
        equity_data[key][percentage] = value.get("percentage")
        equity_data[key][type]
    fig1, ax1 = plt.subplots()
    ax1.pie(equities, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.show()

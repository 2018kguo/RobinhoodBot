# RobinhoodBot
Trading bot for Robinhood accounts

For more info:
https://medium.com/@kev.guo123/building-a-robinhood-stock-trading-bot-8ee1b040ec6a


5/1/19: Since Robinhood has updated it's API, you now have to enter a 2 factor authentication code whenever you run the script. To do this, go to the Robinhood mobile app and enable two factor authentication in your settings. You will now receive an SMS code when you run the script, which you have to enter into the script.



This project supports Python 3.7+


To Install:

```bash
git clone https://github.com/2018kguo/RobinhoodBot.git
cd RobinhoodBot/
pip install -r requirements.txt
cp config.py.sample config.py # add auth info after copying
```

To Run:

```python
cd RobinboodBot/robinhoodbot (If outside of root directory)
python3 main.py
```

import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv('.env')

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API = os.environ['STOCK_API']

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API = os.environ['NEWS_API']

account_sid = os.environ['account_sid']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']
PHONE_NUMBER = os.environ['PHONE_NUMBER']
auth_token = os.environ['auth_token']

stock_parameters = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK_NAME,
    'apikey': STOCK_API
}

news_parameters = {
    'q': COMPANY_NAME,
    'sortBy': 'popularity',
    'apiKey': NEWS_API,
    'language': 'en',
    'searchIn': 'title,description',
}

# Gets the closing stock prices
response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
response.raise_for_status()
data = response.json()['Time Series (Daily)']
data_list = [value for (key, value) in data.items()]

# Gets the closing stock prices for yesterday
yday_closing_price = float(data_list[0]['4. close'])
print(yday_closing_price)

# Gets the closing stock prices for the day before yesterday
before_yday = float(data_list[1]['4. close'])
print(before_yday)

# Calculates the absolute difference in percentage of the two days
price_diff = abs(yday_closing_price - before_yday)
percentage_diff = round((price_diff / yday_closing_price) * 100)
print(percentage_diff)

# If percentage difference is greater than 1, then the News API gets the first 3 articles related to the company.
if percentage_diff > 1:
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    news = news_response.json()['articles'][:3]
    if yday_closing_price > before_yday:
        arrow = '🔺'
    else:
        arrow = '🔻'

    # Creates a list of each article's headline and brief description and formats into a message
    content = [
        f"{STOCK_NAME}: {arrow}{percentage_diff}% \nHeadline: {article['title']} \nBrief: {article['description']} \nTo read more, go to {article['url']}"
        for article in news]
    print(content)

    # Sends each article as a message using Twilio
    client = Client(account_sid, auth_token)
    for item in content:
        message = client.messages \
            .create(
            body=item,
            from_=TWILIO_NUMBER,
            to=PHONE_NUMBER
        )
        print(message.status)

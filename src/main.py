import os
import sys
from datetime import datetime
from time import sleep

import yfinance as yf
import pandas as pd

from src.macd_buy_sell import MACDAnalyzer
from src.ta_util import TAUtil


def get_ohlc_data(ticker, end_date, period):
    csv_filename = os.path.join(os.path.dirname(__file__), '..', 'data', f"{ticker}_ohlc_data.csv")
    data = None
    if os.path.exists(csv_filename):
        print(f"{csv_filename} already exists.")
        data = pd.read_csv(csv_filename)
        # Check if the last candle is today's date
        last_candle_date = pd.to_datetime(data['date'].iloc[-1]).date()
        today_date = pd.to_datetime(datetime.today().strftime('%Y-%m-%d')).date()

        if last_candle_date != today_date:
            print("The data is not current. Downloading new data.")
            data = None

    if data is None:
        data = yf.download(ticker, period=period)
        data.columns = ['_'.join(col).strip() for col in data.columns.values]
        data.rename(columns={
            f'Close_{ticker}': 'close',
            f'High_{ticker}': 'high',
            f'Low_{ticker}': 'low',
            f'Open_{ticker}': 'open',
            f'Volume_{ticker}': 'volume'
        }, inplace=True)
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'date'}, inplace=True)
        data.to_csv(csv_filename)
        # data = pd.read_csv(csv_filename)
        data.set_index('date', inplace=True)
    return data

def check_bullish_signals(df):
    # Bullish signal for RSI: RSI crosses above 30
    df['rsi_bullish'] = (df['rsi'] > 30) & (df['rsi'].shift(1) <= 30)

    # Bullish signal for MACD: MACD line crosses above the signal line
    df['macd_bullish'] = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))

    return df

if __name__ == "__main__":
    today_date = datetime.today().strftime('%Y-%m-%d')

    stocks = ['AAPL', 'NVDA', 'MSFT', 'GOOGL', 'AMZN']
    for stock in stocks:
        ohlc = get_ohlc_data(stock, today_date, '1y')
        macdAnalyzer = MACDAnalyzer()

        analyzed_data = macdAnalyzer.analyze_macd(ohlc)
        signal = macdAnalyzer.get_last_candle_signal(ohlc)
        print("Last Signal:", signal)
        # Plot results
        macdAnalyzer.plot_macd_analysis(analyzed_data, title=f'MACD Analysis of {stock}')

        print(ohlc.tail().to_string())
        sleep(5)

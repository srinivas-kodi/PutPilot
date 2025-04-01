import sys
from datetime import datetime
from time import sleep

import yfinance as yf
import pandas as pd

from src.ta_util import TAUtil


def get_ohlc_data(ticker, end_date, period):
    csv_filename = f"{ticker}_ohlc_data.csv"

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
        ohlc['rsi'] = TAUtil.rsi(ohlc, 14)
        ohlc['macd'], ohlc['macd_signal'] = TAUtil.macd(ohlc,12, 26, 9)

        ohlc = check_bullish_signals(ohlc)

        is_rsi_bullish = ohlc['rsi_bullish'].iloc[-1]
        is_macd_bullish = ohlc['macd_bullish'].iloc[-1]
        print(f"{stock} RSI Bullish: {is_rsi_bullish}, MACD Bullish: {is_macd_bullish}")

        if is_rsi_bullish or is_macd_bullish:
            print(f"Buy signal for {stock} on {today_date}")
            # Sell Put Option

        print(ohlc.tail().to_string())
        sleep(5)

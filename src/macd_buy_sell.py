import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

class MACDAnalyzer:

    def __init__(self):
        pass

    def calculate_macd(self, data, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate MACD, Signal line, and Histogram
        """
        data['EMA_fast'] = data['close'].ewm(span=fast_period, adjust=False).mean()
        data['EMA_slow'] = data['close'].ewm(span=slow_period, adjust=False).mean()
        data['MACD'] = data['EMA_fast'] - data['EMA_slow']
        data['Signal'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
        data['Histogram'] = data['MACD'] - data['Signal']
        return data


    def identify_crossovers(self, data):
        """
        Identify MACD crossovers (bullish/bearish signals)
        """
        data['Signal_Cross'] = 0
        data['Signal_Cross'] = np.where(data['MACD'] > data['Signal'], 1, 0)
        data['Signal_Cross'] = data['Signal_Cross'].diff()
        return data


    def find_divergence(self, data, lookback=5):
        """
        Find bullish and bearish divergences
        """
        # Find price peaks and troughs
        data['Price_High'] = data['high'].rolling(lookback, center=True).max()
        data['Price_Low'] = data['low'].rolling(lookback, center=True).min()

        # Find MACD peaks and troughs
        data['MACD_High'] = data['Histogram'].rolling(lookback, center=True).max()
        data['MACD_Low'] = data['Histogram'].rolling(lookback, center=True).min()

        # Initialize divergence columns
        data['Bullish_Divergence'] = False
        data['Bearish_Divergence'] = False

        # Find bullish divergence (price lower lows, MACD higher lows)
        price_lows = data[data['Price_Low'] == data['low']].index
        for i in range(1, len(price_lows)):
            if (data.loc[price_lows[i], 'low'] < data.loc[price_lows[i - 1], 'low'] and
                    data.loc[price_lows[i], 'MACD_Low'] > data.loc[price_lows[i - 1], 'MACD_Low']):
                data.loc[price_lows[i], 'Bullish_Divergence'] = True

        # Find bearish divergence (price higher highs, MACD lower highs)
        price_highs = data[data['Price_High'] == data['high']].index
        for i in range(1, len(price_highs)):
            if (data.loc[price_highs[i], 'high'] > data.loc[price_highs[i - 1], 'high'] and
                    data.loc[price_highs[i], 'MACD_High'] < data.loc[price_highs[i - 1], 'MACD_High']):
                data.loc[price_highs[i], 'Bearish_Divergence'] = True

        return data


    def analyze_macd(self, data):
        """
        Perform all MACD analysis
        """
        # Calculate MACD components
        data = self.calculate_macd(data)

        # Identify crossovers
        data = self.identify_crossovers(data)

        # Find divergences
        data = self.find_divergence(data)

        return data

    def get_last_candle_signal(self, data):
        """
        Get MACD buy/sell signal for the last candle
        """
        last_signal = None
        last_index = data.index[-1]

        if data['Signal_Cross'].iloc[-1] > 0:
            last_signal = (last_index, 'Buy', 'Trend Reversal Signal')
        elif data['Signal_Cross'].iloc[-1] < 0:
            last_signal = (last_index, 'Sell', 'Trend Reversal Signal')

        if data['Histogram'].iloc[-1] > 0 and data['Histogram'].iloc[-1] > data['Histogram'].iloc[-2]:
            last_signal = (last_index, 'Buy', 'Momentum Confirmation')
        elif data['Histogram'].iloc[-1] < 0 and data['Histogram'].iloc[-1] < data['Histogram'].iloc[-2]:
            last_signal = (last_index, 'Sell', 'Momentum Confirmation')

        if data['Bullish_Divergence'].iloc[-1]:
            last_signal = (last_index, 'Buy', 'Bullish Divergence')
        elif data['Bearish_Divergence'].iloc[-1]:
            last_signal = (last_index, 'Sell', 'Bearish Divergence')

        if data['MACD'].iloc[-1] > 0:
            last_signal = (last_index, 'Buy', 'Overbought Condition')
        elif data['MACD'].iloc[-1] < 0:
            last_signal = (last_index, 'Sell', 'Oversold Condition')

        return last_signal

    def plot_macd_analysis(self, data, title='MACD Analysis'):
        """
        Plot price chart with MACD and signals
        """
        plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(3, 1, height_ratios=[3, 1, 1])

        # Price chart
        ax0 = plt.subplot(gs[0])
        ax0.plot(data['close'], label='Price', color='black')

        # Plot bullish crossovers (MACD crosses above Signal)
        bullish_cross = data[data['Signal_Cross'] > 0]
        ax0.scatter(bullish_cross.index, bullish_cross['close'],
                    color='green', marker='^', label='Bullish Crossover')

        # Plot bearish crossovers (MACD crosses below Signal)
        bearish_cross = data[data['Signal_Cross'] < 0]
        ax0.scatter(bearish_cross.index, bearish_cross['close'],
                    color='red', marker='v', label='Bearish Crossover')

        # Plot divergences
        bullish_div = data[data['Bullish_Divergence']]
        ax0.scatter(bullish_div.index, bullish_div['close'],
                    color='blue', marker='*', s=100, label='Bullish Divergence')

        bearish_div = data[data['Bearish_Divergence']]
        ax0.scatter(bearish_div.index, bearish_div['close'],
                    color='orange', marker='*', s=100, label='Bearish Divergence')

        ax0.set_title(title)
        ax0.legend()

        # MACD line and signal line
        ax1 = plt.subplot(gs[1], sharex=ax0)
        ax1.plot(data['MACD'], label='MACD', color='blue')
        ax1.plot(data['Signal'], label='Signal', color='red')
        ax1.axhline(0, color='gray', linestyle='--')
        ax1.legend()

        # MACD histogram
        ax2 = plt.subplot(gs[2], sharex=ax0)
        ax2.bar(data.index, data['Histogram'],
                color=np.where(data['Histogram'] > 0, 'green', 'red'))
        ax2.axhline(0, color='gray', linestyle='--')

        plt.tight_layout()
        plt.show()

# Example usage:
# Assuming you have an OHLC DataFrame called 'ohlc_data'
# ohlc_data = pd.read_csv('your_data.csv', parse_dates=True, index_col=0)

# Perform MACD analysis
# analyzed_data = analyze_macd(ohlc_data)

# Plot results
# plot_macd_analysis(analyzed_data, title='MACD Analysis of Your Asset')


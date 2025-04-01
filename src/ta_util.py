import numpy as np


class TAUtil:
    def __init__(self):
        pass

    @staticmethod
    def rsi(df, n):
        "function to calculate RSI"
        delta = df["close"].diff().dropna()
        u = delta * 0
        d = u.copy()
        u[delta > 0] = delta[delta > 0]
        d[delta < 0] = -delta[delta < 0]
        u[u.index[n - 1]] = np.mean(u[:n])  # first value is average of gains
        u = u.drop(u.index[:(n - 1)])
        d[d.index[n - 1]] = np.mean(d[:n])  # first value is average of losses
        d = d.drop(d.index[:(n - 1)])
        rs = u.ewm(com=n, min_periods=n).mean() / d.ewm(com=n, min_periods=n).mean()

        rsi = 100 - 100 / (1 + rs)
        return rsi

    @staticmethod
    def macd(DF, a=12, b=26, c=9):
        """function to calculate MACD
           typical values a(fast moving average) = 12;
                          b(slow moving average) =26;
                          c(signal line ma window) =9"""
        df = DF.copy()
        df["MA_Fast"] = df["close"].ewm(span=a, min_periods=a).mean()
        df["MA_Slow"] = df["close"].ewm(span=b, min_periods=b).mean()
        df["macd"] = df["MA_Fast"] - df["MA_Slow"]
        df["signal"] = df["macd"].ewm(span=c, min_periods=c).mean()
        # df.dropna(inplace=True)
        df.drop(['MA_Fast', 'MA_Slow'], axis=1, inplace=True)
        # return df
        return df["macd"], df["signal"]
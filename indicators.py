"""Technical indicators computed directly with pandas/numpy (no extra dependencies)."""

import pandas as pd


def moving_average(df, window=20, column="Close"):
    return df[column].rolling(window=window).mean()


def bollinger_bands(df, window=20, num_std=2, column="Close"):
    ma = df[column].rolling(window=window).mean()
    std = df[column].rolling(window=window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return pd.DataFrame({"BB_Mid": ma, "BB_Upper": upper, "BB_Lower": lower})


def rsi(df, window=14, column="Close"):
    delta = df[column].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi_values = 100 - (100 / (1 + rs))
    rsi_values[avg_loss == 0] = 100
    rsi_values[(avg_gain == 0) & (avg_loss == 0)] = 50
    return rsi_values


def macd(df, fast=12, slow=26, signal=9, column="Close"):
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({"MACD": macd_line, "Signal": signal_line, "Histogram": histogram})

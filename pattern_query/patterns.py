import pandas as pd

def detect_patterns(df):
    # Simple example: detect Doji candlestick (close ~ open)
    df["doji"] = abs(df["close"] - df["open"]) < (df["high"] - df["low"]) * 0.1
    patterns = df[df["doji"]]
    return patterns

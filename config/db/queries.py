import pandas as pd

def fetch_ohlc_data(conn, symbol):
    query = f"""
        SELECT date, open, high, low, close, volume
        FROM stock_ohlc
        WHERE symbol = %s
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn, params=(symbol,))
    return df

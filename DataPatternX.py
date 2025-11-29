import os
from config.config import load_config
from db.connection import get_connection
from db.queries import fetch_ohlc_data
from pattern_query.patterns import detect_patterns
from plotter.plot_chart import plot_candlestick_chart

def main():
    # Load config
    config = load_config()

    # Connect to DB
    conn = get_connection(config)

    # Fetch OHLC data from DB
    data = fetch_ohlc_data(conn, symbol="RELIANCE")

    # Detect candlestick patterns
    pattern_results = detect_patterns(data)

    # Plot results
    plot_candlestick_chart(data, pattern_results, title="RELIANCE Candlestick Analysis")

if __name__ == "__main__":
    main()

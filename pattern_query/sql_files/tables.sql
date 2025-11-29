CREATE TABLE stocks (
    stock_id SERIAL PRIMARY KEY,
    stock_symbol VARCHAR(16) UNIQUE NOT NULL,
    stock_name VARCHAR(500),
    stock_exchange VARCHAR(10),
    stock_group VARCHAR(10)
);

CREATE TABLE candlesticks (
    candle_id SERIAL PRIMARY KEY,
    stock_id INT NOT NULL REFERENCES stocks(stock_id) ON DELETE CASCADE,
    candle_date TIMESTAMP NOT NULL,
    open_price NUMERIC(16,4) NOT NULL,
    high_price NUMERIC(16,4) NOT NULL,
    low_price NUMERIC(16,4) NOT NULL,
    close_price NUMERIC(16,4) NOT NULL,
    prev_close_price NUMERIC(16,4) NOT NULL,
    number_of_trades BIGINT,
    number_of_shares BIGINT,
    net_turnover NUMERIC(16,4),
    UNIQUE(stock_id, candle_date)
);

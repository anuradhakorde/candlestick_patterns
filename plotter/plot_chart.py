import plotly.graph_objects as go

def plot_candlestick_chart(df, patterns, title="Candlestick Chart"):
    fig = go.Figure(data=[go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])

    # Highlight Doji patterns as example
    fig.add_trace(go.Scatter(
        x=patterns['date'],
        y=patterns['high'] + 1,
        mode='markers',
        name='Doji',
        marker=dict(color='orange', size=10, symbol='circle')
    ))

    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price")
    fig.show()

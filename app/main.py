import re
from datetime import timedelta

import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from chart import get_candlestick_fig
from core.candlestick_recognition import recognize_candlestick, candle_patterns, is_support, is_resistance

st.set_page_config(layout="wide")

symbol = st.sidebar.text_input("Symbol", value="BTC-USD", max_chars=None, key=None, type='default')
interval = st.sidebar.selectbox('Interval',
                                ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo",
                                 "3mo"), index=3)
period = st.sidebar.selectbox('Period',
                              ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"), index=0)

st.subheader(symbol.upper())
with st.spinner('Loading symbol...'):
    df = yf.download(tickers=symbol, period=period, interval=interval)
    new_df = recognize_candlestick(df)
    fig = get_candlestick_fig(new_df)

    if df.empty:
        st.error(f"I haven't found any data for the symbol : '{symbol}', please check if this symbol exists:", icon="🚨")
        st.link_button("Stocks list", "https://www.nasdaq.com/market-activity/stocks/screener")
        st.link_button("Cryptocurrencies list", "https://coinmarketcap.com/all/views/all/")
        exit()

fig.add_trace(go.Scatter(x=new_df.index, y=new_df["Open"], mode="lines", name="Open", visible='legendonly'))
fig.add_trace(go.Scatter(x=new_df.index, y=new_df["Close"], mode="lines", name="Close", visible='legendonly'))
fig.add_trace(go.Scatter(x=new_df.index, y=new_df["High"], mode="lines", name="High", visible='legendonly'))
fig.add_trace(go.Scatter(x=new_df.index, y=new_df["Low"], mode="lines", name="Low", visible='legendonly'))

step = int("".join(re.findall("[\d]+", interval)))
time_step = "".join(re.findall("[a-zA-Z]+", interval))
converter = 1
if time_step == "m":
    unit = "minutes"
    converter = 1
if time_step == "h":
    unit = "hours"
    converter = 60
if time_step == "d":
    unit = "days"
    converter = 24 * 60
if time_step == "wk":
    unit = "W"
    converter = 7 * 24 * 60
if time_step == "mo":
    unit = "m"
    converter = 4 * 7 * 24 * 60

EMA20 = new_df["Close"].ewm(halflife=f"20 {unit}", times=new_df.index).mean()
fig.add_trace(go.Scatter(x=new_df.index, y=EMA20, mode="lines", name="EMA20", visible='legendonly'))

fig_to_add = [dict(label="None", method="relayout", args=["shapes", []])]
for elem in candle_patterns:
    subset = new_df[new_df["candlestick_pattern"] == elem["pattern"]]
    lower_bound = timedelta(minutes=step * converter * (elem["number"] - 1) + 0.5 * step * converter)
    upper_bound = timedelta(minutes=0.5 * step * converter)
    if subset.shape[0] != 0:
        patterns = []
        for index, row in subset.iterrows():
            x0 = index - lower_bound
            x1 = index + upper_bound
            y0 = row["Low"]
            y1 = row["High"]
            pattern = dict(type="rect", xref="x", yref="y", x0=x0, y0=y0, x1=x1, y1=y1,
                           line=dict(color=elem["color"]))
            patterns.append(pattern)
        fig_to_add.append(dict(label=elem["name"],
                               method="relayout",
                               args=["shapes", patterns]))

## Supports & Resistances pattern recognition
supports = []
resistances = []
for i in range(2, df.shape[0] - 2):
    if is_support(df, i):
        supports.append((i, df['Low'].iloc[i]))
    elif is_resistance(df, i):
        resistances.append((i, df['High'].iloc[i]))

support_patterns = []
for support in supports:
    pattern = dict(type="line", xref="x", yref="y",
                   x0=df.index[support[0]],
                   y0=support[1],
                   x1=max(df.index),
                   y1=support[1],
                   line=dict(color="RoyalBlue", width=1,),
                   )
    support_patterns.append(pattern)

fig_to_add.append(dict(label="supports",
                       method="relayout",
                       args=["shapes", support_patterns]))
resistance_patterns = []
for resistance in resistances:
    pattern = dict(type="line", xref="x", yref="y",
                   x0=df.index[resistance[0]],
                   y0=resistance[1],
                   x1=max(df.index),
                   y1=resistance[1],
                   line=dict(color="DarkOrange", width=1, ),
                   )
    resistance_patterns.append(pattern)

fig_to_add.append(dict(label="resistances",
                       method="relayout",
                       args=["shapes", resistance_patterns]))

fig.update_layout(
    updatemenus=[
        dict(buttons=fig_to_add)
    ]
)

st.plotly_chart(fig, use_container_width=True)
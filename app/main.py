import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import plotly.graph_objects as go
from datetime import timedelta, date
import re

# Custom import
from core.candlestick_recognition import recognize_candlestick, candle_patterns, isSupport, isResistance
from chart import get_candlestick_fig

st.set_page_config(layout="wide")

# symbol = st.sidebar.text_input("Symbol", value='BTC-EUR', max_chars=None, key=None, type='default')
symbol = st.sidebar.selectbox('Currency', ("AXS-USD", "LUNA1-USD", "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "VET-USD"),
                              index=0)
interval = st.sidebar.selectbox('Interval',
                                ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo",
                                 "3mo"), index=3)
period = st.sidebar.selectbox('Period',
                              ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"), index=0)

st.subheader(symbol.upper())
with st.spinner('Loading classification model...'):
    df = yf.download(tickers=symbol, period=period, interval=interval)
    new_df = recognize_candlestick(df)
    fig = get_candlestick_fig(new_df)

fig.add_trace(go.Scatter(x=new_df.index, y=new_df["Open"], mode="lines", name="Open", visible='legendonly'))
fig.add_trace(go.Scatter(x=new_df.index, y=new_df["Close"], mode="lines", name="Close", visible='legendonly'))
fig.add_trace(go.Scatter(x=new_df.index, y=new_df["High"], mode="lines", name="High", visible='legendonly'))
fig.add_trace(go.Scatter(x=new_df.index, y=new_df["Low"], mode="lines", name="Low", visible='legendonly'))

step = int("".join(re.findall("[\d]+", interval)))
time_step = "".join(re.findall("[a-zA-Z]+", interval))
converter = 1
if time_step == "m":
    a = "minutes"
    converter = 1
if time_step == "h":
    a = "hours"
    converter = 60
if time_step == "d":
    a = "days"
    converter = 24 * 60
if time_step == "wk":
    a = "weeks"
    converter = 7 * 24 * 60
if time_step == "mo":
    a = "months"
    converter = 4 * 7 * 24 * 60

# SMA100 = new_df["Close"].rolling(str(100) + "d", min_periods=1).mean()
# SMA10 = new_df["Close"].rolling(str(10) + "d", min_periods=1).mean()
# SMA5 = new_df["Close"].rolling(str(5) + time_step, min_periods=1).mean()

EMA20 = new_df["Close"].ewm(halflife='20 ' + str(a), times=new_df.index).mean()

# fig.add_trace(go.Scatter(x=new_df.index, y=SMA5, mode="lines", name="SMA5", visible='legendonly'))
# fig.add_trace(go.Scatter(x=new_df.index, y=SMA10, mode="lines", name="SMA10", visible='legendonly'))
# fig.add_trace(go.Scatter(x=new_df.index, y=SMA100, mode="lines", name="SMA100", visible='legendonly'))
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
    if isSupport(df, i):
        supports.append((i, df['Low'][i]))
    elif isResistance(df, i):
        resistances.append((i, df['High'][i]))
patterns = []
for support in supports:
    pattern = dict(type="line", xref="x", yref="y",
                   x0=df.index[support[0]],
                   y0=support[1],
                   x1=max(df.index),
                   y1=support[1],
                   line=dict(color="RoyalBlue", width=1,),
                   )
    patterns.append(pattern)
fig_to_add.append(dict(label="supports",
                       method="relayout",
                       args=["shapes", patterns]))
for resistance in resistances:
    pattern = dict(type="line", xref="x", yref="y",
                   x0=df.index[resistance[0]],
                   y0=resistance[1],
                   x1=max(df.index),
                   y1=resistance[1],
                   line=dict(color="DarkOrange", width=1, ),
                   )
    patterns.append(pattern)
fig_to_add.append(dict(label="resistances",
                       method="relayout",
                       args=["shapes", patterns]))

fig.update_layout(
    updatemenus=[
        dict(buttons=fig_to_add)
    ]
)

st.plotly_chart(fig, use_container_width=True)
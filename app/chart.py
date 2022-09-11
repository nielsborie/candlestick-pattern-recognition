import plotly.graph_objects as go


def get_candlestick_fig(df):
    candlestick = [go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="candlestick")]

    layout = go.Layout(
        yaxis=dict(fixedrange=False),
        xaxis={'rangeselector': {'buttons': [{'count': 7,
                                                             'label': '1w',
                                                             'step': 'day',
                                                             'stepmode': 'backward'},
                                                            {'count': 1,
                                                             'label': '1d',
                                                             'step': 'day',
                                                             'stepmode': 'backward'},
                                                            {'count': 4,
                                                             'label': '4h',
                                                             'step': 'hour',
                                                             'stepmode': 'backward'},
                                                            {'count': 1,
                                                             'label': '1h',
                                                             'step': 'hour',
                                                             'stepmode': 'backward'},
                                                            {'count': 15,
                                                             'label': '15m',
                                                             'step': 'minute',
                                                             'stepmode': 'backward'},
                                                            {'count': 5,
                                                             'label': '5m',
                                                             'step': 'minute',
                                                             'stepmode': 'backward'},
                                                            {'step': 'all'},
                                                            ]},
                              'rangeslider': {'visible': True}})

    fig = go.Figure(data=candlestick, layout=layout)
    return fig

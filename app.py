# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from datetime import date, timedelta
import datetime
import dash
import requests
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import pdb
from dash.dependencies import Input, Output
import plotly.graph_objects as go



now = datetime.datetime.now().isoformat()
start_time = (datetime.datetime.now() - timedelta(days=4)).isoformat()

# The granularity field must 
# be one of the following values: {60, 300, 900, 3600, 21600, 86400}. 
# Otherwise, your request will be rejected. 
# These values correspond to timeslices representing one minute, 
# five minutes, fifteen minutes, 
# one hour, six hours, and one day, respectively.



granularity = '3600'


# url = f'https://api.pro.coinbase.com/products/BTC-EUR/candles?granularity={granularity}'
url = f'https://api.pro.coinbase.com/products/BTC-EUR/candles?start={start_time}&end={now}&granularity={granularity}'

response = requests.get(url).json()
# pdb.set_trace()

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)

colors = {
    'background': '#2F4B6C',
    'text': '#F0F2F6',
    'starting-price': '#8EA1BF',
    'buy-price': '#6DEAC7',
    'sell-price': '#F7931A'
}

# display current Bitcoin / Euro prices as a bar chart with hours on bottom axis
# first figure out how to get the data with API calls

# then build a plotly scatterplot for this and display it

# make the plot look nice 

# add a line for buy PTC and sell PTC 

# the line should have a dot where it intersects with the graph and this should have a label saying what happens when

# add a slider so you can change the value of this 

times = [datetime.datetime.fromtimestamp(x[0]).strftime("%b %d %H:%M") for x in response]
times.reverse()

# [print(x) for x in response]
# print(times)


# prices value is the high price in the response object
prices = [x[2] for x in response]
prices.reverse()

# pdb.set_trace()

fig = px.line(
    x=times, y=prices, title="Choose a Buy and Sell BTC to see how Finnly works", height=325
)

fig.update_xaxes(showgrid=False, title="", showticklabels=True)
fig.update_yaxes(showgrid=False, title="Euros")



# add tick values

fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = times[::12],
        ticktext = times[::12]
    ),

)

formatted_starting_price = (format (prices[0], ',d'))



# add starting price line

fig.add_trace(go.Scatter(
    x=[times[0], times[-1]],
    y=[prices[0], prices[0]],
    name=f'Starting Price - €{formatted_starting_price}',
    line=dict(color=colors['starting-price'])
))


fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)


app.layout = html.Div([
    html.Div(style={'columnCount': 2, 'margin': 50}, children=[
        html.Label('Buy Price Trigger Control (PTC)'),
        dcc.Slider(
            min=0,
            max=3,
            id='buy-slider',

            marks={
                0: '',
                1: '-1%',
                2: '-2%',
                3: '-3%'
            },
            value=0,
        ),
        html.Label('Sell Price Trigger Control (PTC)'),
        dcc.Slider(
            min=0,
            max=3,
            id='sell-slider',
            marks={
                0: '',
                1: '+1%',
                2: '+2%',
                3: '+3%'
            },
            value=0,
        )
    ]),
    dcc.Graph(id="graph-with-slider", figure=fig),
    html.Pre(
        id='structure',
        style={
            'border': 'thin lightgrey solid', 
            'overflowY': 'scroll',
            'height': '275px'
        }
    )
])

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('buy-slider', 'value'))


def update_figure(selected_value):
    
    if selected_value == 1:
        buy_price = int(prices[0] - (prices[0] * .01))
        formatted_buy_price = (format (buy_price, ',d'))
        fig.update_layout(title_text=f"Finnly will buy at €{formatted_buy_price}")
        fig.add_trace(go.Scatter(
            x=[times[0], times[-1]],
            y=[buy_price, buy_price],
            name=f'Buy PTC Price - €{formatted_buy_price}',
            line=dict(color=colors['buy-price'])
        ))
        

    else:
        fig.update_layout(title_text="Choose a Buy and Sell BTC to see how Finnly works")


    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
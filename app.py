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


# now = datetime.datetime.now().isoformat()
now = datetime.datetime(2021, 2, 11, 15, 0, 0, 0).isoformat()

start_time = (datetime.datetime(2021, 2, 11, 15, 0, 0, 0) - timedelta(hours=30)).isoformat()

# The granularity field must 
# be one of the following values: {60, 300, 900, 3600, 21600, 86400}. 
# Otherwise, your request will be rejected. 
# These values correspond to timeslices representing one minute, 
# five minutes, fifteen minutes, 
# one hour, six hours, and one day, respectively.



granularity = '900'


# url = f'https://api.pro.coinbase.com/products/BTC-EUR/candles?granularity={granularity}'
url = f'https://api.pro.coinbase.com/products/BTC-EUR/candles?start={start_time}&end={now}&granularity={granularity}'

response = requests.get(url).json()
# pdb.set_trace()

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)

colors = {
    'background': '#2F4B6C',
    'text': '#F0F2F6',
    'starting-price': '#F0F2F6',
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

formatted_starting_price = (format (int(prices[0]), ',d'))

buy_price = int(prices[0] - (prices[0] * .01))
formatted_buy_price = (format (buy_price, ',d'))

sell_price = int(prices[0] + (buy_price * .01))
formatted_sell_price = (format (sell_price, ',d'))

distance_from_buy_price_array = [price - buy_price for price in prices]





# helper methods to find first negative/positive number in array

def first_neg(list):
    count = 0
    for number in list:
        count += 1
        if number < 0:
            return count


index_of_closest_buy_price = first_neg(distance_from_buy_price_array)


# take the prices after the buy price and for each one calculate 


distance_from_sell_price_array = [sell_price - price for price in prices[index_of_closest_buy_price::]]


index_of_closest_sell_price = first_neg(distance_from_sell_price_array)

# pdb.set_trace()

# add starting price line

fig.add_trace(go.Scatter(
    x=[times[0]],
    y=[prices[0]],
    name=f'Starting Price',
    line=dict(color=colors['starting-price']),
    marker=dict(size=10)
))



# map elements in array
# for each price do this price - buy price
# find closest result that is a minus number
# get the index of it
# the value you want is this index in the real array

# add buy ptc line
# this should be a dot where finnly will buy (or could have a line up to this dot)
# how to find the dot where he will buy?
# have the line stop at the closest data point
# find the element in the times array where the

fig.add_trace(go.Scatter(
            x=[times[index_of_closest_buy_price]],
            y=[buy_price],
            name='Buy PTC Price',
            line=dict(color=colors['buy-price']),
            marker=dict(size=10)
        ))



sell_index = index_of_closest_sell_price + index_of_closest_buy_price
# pdb.set_trace()
# add sell ptc line
fig.add_trace(go.Scatter(
            x=[times[sell_index]],
            y=[sell_price, sell_price],
            name='Sell PTC Price',
            line=dict(color=colors['sell-price']),
            marker=dict(size=10)
        ))

# pdb.set_trace()

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

def calculate_buy_price(value):
    percentage = value / 100.0
    buy_price = int(prices[0] - (prices[0] * percentage))
    return buy_price

def calculate_sell_price(buy_price, percent):
    percent_as_float = percent / 100.0
    sell_price = int(buy_price - (buy_price * -percent_as_float))
    return sell_price


def calculate_new_index(value, buy=True, **kwargs):
    if buy:
        buy_price = calculate_buy_price(value)
        distance_from_buy_price_array = [price - buy_price for price in prices]
        index_of_closest_buy_price = first_neg(distance_from_buy_price_array)
        return index_of_closest_buy_price
    else:
        buy_price = kwargs['buy_price']
        distance_from_buy_price_array = [price - buy_price for price in prices]
        index_of_closest_buy_price = first_neg(distance_from_buy_price_array)
        sell_price = calculate_sell_price(buy_price, value)
        distance_from_sell_price_array = [sell_price - price for price in prices[index_of_closest_buy_price::]]
        index_of_closest_sell_price = first_neg(distance_from_sell_price_array)
        return index_of_closest_buy_price + index_of_closest_sell_price

def format_price(value):
    return format (int(value), ',d')

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('buy-slider', 'value'),
    Input('sell-slider', 'value'))

def update_figure(buy_value, sell_value):
    if buy_value > 0 and sell_value > 0:
        # pdb.set_trace()
        fig.for_each_trace(
            lambda trace: trace.update(x=[times[calculate_new_index(buy_value)]],
            y=[calculate_buy_price(buy_value)]) if trace.name == "Buy PTC Price" else ()
        )
        fig.for_each_trace(
            lambda trace: trace.update(x=[times[calculate_new_index(sell_value, False, buy_price=calculate_buy_price(buy_value))]],
            y=[calculate_sell_price(calculate_buy_price(buy_value), sell_value)]) if trace.name == "Sell PTC Price" else ()
        )
        fig.update_layout(title_text=f"Finnly buys 1 Bitcoin at €{format_price(calculate_buy_price(buy_value))} and sells it at €{format_price(calculate_sell_price(calculate_buy_price(buy_value), sell_value))} making a total of €{format_price(calculate_sell_price(calculate_buy_price(buy_value), sell_value) - calculate_buy_price(buy_value))} profit 💰")
    else:
        fig.update_layout(title_text="Choose a Buy and Sell PTC to see how Finnly can perform on a trade run")

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
# Description: Web application for the Cat Door App. Pulls data from aggregate_data.txt file and 
#  plots it on a graph using Plotly Dash.
# Date: Oct 11 2022
# Author: Vanessa Pesch
#
# Note: this was deployed with Heroku free tier, which Heroku has since eliminated.

from dash import Dash, html, dcc, Input, Output
import numpy as np
import pandas as pd
import plotly.express as px
import os

app = Dash(__name__, title="Cat Door App") # Website title in browser title bar

server = app.server # Declare server for Heroku deployment

df = pd.DataFrame({'results':[]}, index=[]) # Create pandas dataframe

cwd = os.getcwd() # Current working directory

# Open aggregate_data.txt file. Its contents should have a data in the first column,
# and one or many subsequent columns containing numbers (that represent time spent outside).
with open (cwd+'/data/logs/aggregate_data.txt', 'r') as temp:
    lines = temp.readlines() # Read lines
    # For each line, add only the first and last column to the dataframe
    # Source code: https://stackoverflow.com/a/52890095
    for row in lines: 
        df.loc[row.split(',')[0]]=[row.split(',')[-1].replace('\n','')]

# Convert the index column of the dataframe to datetime format
# Source code: https://stackoverflow.com/a/60528830
df.index = pd.to_datetime(df.index, format='%Y%m%d')

# Convert results column of the dataframe to numeric type 
df['results'] = pd.to_numeric(df['results'])

# Create a new dataframe that has two columns: 1) year and month, and 2) average results of that month
# Source code: https://stackoverflow.com/a/67853478
df_date = df.set_index(df.index, inplace=False)
df_mean = df_date.resample('M').mean()

# Convert the time in 'results' column from minutes to hours
df_mean['results'] = pd.to_datetime(df_mean['results'], unit='m').dt.strftime('%-H.%-M')

# Create bar graph using df_month dataframe
fig_monthly = px.bar(df_mean, x=df_mean.index, y=df_mean.loc[:,'results'].astype(float),color='results', color_discrete_sequence=px.colors.qualitative.Plotly)
# Display only one value on the x axis for each month
# Source code: https://plotly.com/python/reference/#dtick
fig_monthly.update_layout(xaxis=dict(tickformat='%b %Y',tick0=df_mean.index[0],dtick='M1'))

# Convert to hours
df['results'] = pd.to_datetime(df['results'], unit='m').dt.strftime('%-H.%-M')
# Create bar graph using df dataframe
fig_daily = px.bar(df, x=df.index, y=df.loc[:,'results'].astype(float),color='results', color_discrete_sequence=px.colors.qualitative.Bold)

# Change style of graph. Parameters:
#      -fig - the figure or graph to be displayed
def style_graph(fig):
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Hours',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis_title_font_size=18,
        yaxis_title_font_size=18,
        # Change color of rangeselector.
        # Source code: https://stackoverflow.com/a/72533537
        xaxis=dict(
            rangeselector = dict(activecolor='#EFC050',font_color="black")
        )
    )
    # Create rangeselector buttons for '1 month', '6 months', '1 year' and 'all' views.
    # Source code: https://plotly.com/python/time-series/#time-series-with-range-selector-buttons
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1,label='1m', step='month', stepmode='backward'),
                dict(count=6,label='6m', step='month', stepmode='backward'),
                dict(count=1,label='1y', step='year', stepmode='backward'),
                dict(step='all')
            ])
        )
    )
    # Remove side legend and colorbar
    fig.update(layout_showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    # Change hover text.Source code: https://plotly.com/python/hover-text-and-formatting
    fig.update_traces(hovertemplate='Date: %{x} <br>%{y}<extra></extra> hours')
    return fig

style_graph(fig_monthly) # Style the monthly averages graph

style_graph(fig_daily) # Style the daily graph

        
# Create website structure
app.layout = html.Div([
    html.Div( # Header containing website title
        className='header',
        children=[
            html.H1('Cat Door App')
        ]
    ),
    html.Div( # Brief description of the website and radio buttons selectable by user
        className='description',
        children=[
            html.H2('View how much time Sylvester spent outside:'),
            dcc.RadioItems(
                ['Daily','Monthly Average'],
                'Daily',
                id='graph-select',
                inline=True
            )
        ]
    ),
    html.Div( # Graph of the data
         className='graph',
         children=[
            dcc.Graph(
                id='cat-graph'
            )
         ]
    )
])

# Callback function for the radio buttons.
# When user selects 'Daily" or 'Monthly Average' button, calls update_graph() function.
@app.callback(
    Output('cat-graph', 'figure'),
    Input('graph-select','value')
)

# Create graph with data selected by user through parameter graph_select. 
# Parameters:
#     -graph-select - the radio button selected by user
def update_graph(graph_select):
    
    if graph_select == 'Daily':
        return fig_daily
    else:
        return fig_monthly


if __name__ == '__main__':
    app.run_server(debug=True)


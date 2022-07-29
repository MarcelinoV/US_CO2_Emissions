from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go 
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os

from pytz import timezone
from database.database import *
from utils import *

# create database

conn = create_table()

# build logging and scheduler

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# cronjob

cron_scheduler = BackgroundScheduler(daemon=True)

# load data

data = load_data()

emissions = preprocess(data)

unused = integrity_check(emissions)

# beginning of app

app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
server = app.server

app.layout = html.Div([html.H4('United States CO2 Emissions by Energy Sector'),

    html.P('''This dashboard displays a SARIMA (Seasonal Autoregressive Integrated Moving Average) Time Series Model
    of yearly total United States Greenhouse Gas Emissions in CO2e, or Carbon Dioxide Equivalent Value. Carbon dioxide equivalent 
    or CO2e means the number of metric tons of CO2 emissions with the same global warming potential as one metric ton of another greenhouse gas.
    
    In future updates, this dashboard will include a heatmap of the United States showing where most of these emissions come from, as well as
    a table of model statistics, graphical summary of model evaluation and error analysis, and a list of sources.
    '''),
    html.P('Author: Marcelino Velasquez'),
    html.P([html.A('Data Source - EPA Envirofacts API', href='https://www.epa.gov/enviro/envirofacts-data-service-api')]),
    html.P([html.A('LinkedIn', href='https://www.linkedin.com/in/marcelino-velasquez-739b4013b/')]),
    html.P([html.A('GitHub', href='https://github.com/MarcelinoV')]),
#]), 

html.Div([
    dcc.Graph(id='time_series_chart'),
    html.P('Select Sector'),
    dcc.Dropdown(
        id='sector',
            options=[i for i in emissions.columns if i not in unused],
            value='Chemicals',
            clearable=False,
    ),

])])

@app.callback(
    Output('time_series_chart', 'figure'),
    Input('sector', 'value'))

def display_time_series(sector):
    results = sector_co2_forecast(emissions, sector)
    sec_series = emissions[sector]
    # forecasting
    
    # get forecast for 10 years

    forecast = results.get_forecast(steps=10)

    # get confidence intervals

    forecast_ci = forecast.conf_int()

    # combine observed and forecasted

    final_ts = pd.concat([sec_series, forecast.predicted_mean])

    # create x axis of dates

    last_date = emissions.index[-1]
    date_list = [i + int(last_date) for i in range(len(forecast.predicted_mean)+1)]

    x_axis = list(set(list(emissions.index) + date_list))

    # figure
    fig = go.Figure()

    # forecasted values
    fig.add_trace(go.Scatter(x=x_axis, y=final_ts, name='Forecast', line={'color':'red'}, mode='lines+markers'))

    # upper bound CI
    fig.add_trace(go.Scatter(x=x_axis[-10:], 
                            y=forecast_ci.iloc[:,1], 
                            name="95% CI Upper", 
                            line=dict(width=0), 
                            mode='lines', 
                            showlegend=False))

    # lower bound CI
    fig.add_trace(go.Scatter(x=x_axis[-10:], 
                            y=forecast_ci.iloc[:,0], 
                            name="95% CI Lower", 
                            line=dict(width=0), 
                            mode='lines',
                            fill='tonexty',
                            fillcolor='rgba(0, 50, 0, 0.3)',
                            showlegend=False))

    # observed values
    fig.add_trace(go.Scatter(x=x_axis, y=sec_series, name="Observed", line={'color':'blue'}))

    # graph formatting
    fig.update_layout(
        title=f'{sec_series.name} CO2 Emissions from {min(x_axis)}-{max(x_axis)}',
        xaxis_title='Time (year)',
        yaxis_title=f'{sec_series.name} Emissions in CO2e Value',
        legend_title="",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
        ),
        xaxis= dict(
            type='category',
            tickmode='array',
            tickvals=x_axis,
            ticktext=x_axis
        ),
        hovermode='x'
    )

    return fig

if __name__ == '__main__':

    df = pd.read_pickle(r'database/backup.pkl')
    insert_data(df, conn)
    cron_scheduler.add_job(lambda: update_data(api_call()), trigger='cron', month='1-12', day='1', timezone='America/New_York')
    cron_scheduler.start()
    app.run_server(debug=True)

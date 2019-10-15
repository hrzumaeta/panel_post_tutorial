#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import param
import datetime as dt
import panel as pn
from statsmodels.tsa.arima_model import ARIMA

from bokeh.models import HoverTool, SaveTool, PanTool, CrosshairTool
from bokeh.models.formatters import NumeralTickFormatter,DatetimeTickFormatter
from bokeh.plotting import figure

from time import strptime

pn.extension()

class panel_class(param.Parameterized):
    
    title = 'Forecasting Airline Passengers'
    subtitle = pn.pane.Str('Actual vs ARIMA Model', style={'font-size': '15pt'})
    
    date_slider = pn.widgets.DateRangeSlider(
    name='Date Range Slider',
    start=dt.datetime(1949, 1, 1), end=dt.datetime(1960, 12, 1),
    value=(dt.datetime(1949, 1, 1), dt.datetime(1960, 12, 1)),width=300,
     bar_color='#D15555')
    
    def get_data(self):
        df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/flights.csv')
        df['month'] = df['month'].apply(lambda x: strptime(x,'%B').tm_mon)
        df['date'] = df[['year', 'month']].\
            apply(lambda x: '-'.join(x.astype(str)), axis=1)+'-01'
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df[['date','passengers']]
        self.data_frame = df.copy()
    
    @param.depends('date_slider.value')
    def arima_model(self):
        df_model = self.data_frame.copy()
        df_model = df_model.set_index(pd.DatetimeIndex(df_model['date'],freq='MS')).drop('date',axis=1)
        df_model = df_model[df_model.index > self.date_slider.value[0]] 
        df_model = df_model[df_model.index < self.date_slider.value[1]]
        model = ARIMA(df_model, order=(0,1,1),freq='MS') # basic exponential smoothing model
        model_fit = model.fit(disp=0)

        fitted_df = df_model.copy().rename({'passengers':'actual'},axis=1)
        fitted_df['fitted'] = model_fit.predict(typ='levels') 
        fitted_df['error'] = abs(fitted_df['actual'] - fitted_df['fitted'])
        fitted_df['perc_error'] = fitted_df['error']/fitted_df['actual']
        fitted_df.reset_index(inplace=True,drop=False)
                
        p = figure(plot_width=800, plot_height=266)
        p.line('date','actual',source=fitted_df, legend='Actual', color='red')
        glyph = p.line('date','fitted',source=fitted_df, legend='Fitted', color='blue')       
        p.yaxis.formatter = NumeralTickFormatter(format="0,0")
        p.xaxis.formatter = DatetimeTickFormatter(months = "%m/%Y")
        p.title.text = 'Actual vs Fitted ARIMA Values'
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Passengers'
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        hover = HoverTool(renderers=[glyph],
         tooltips=[     ("Date","@date{%F}"),
                        ("Fitted","@fitted"),
                        ("Actual","@actual")],
                  formatters={"date": "datetime"},
              mode='vline'
         )
        p.tools = [SaveTool(), PanTool(), hover, CrosshairTool()]
        return p
    
    @param.depends('title')
    def header(self):
        title_panel = pn.pane.Str(self.title, style={'font-size': '20pt'})
        return  title_panel
    
    @param.depends('subtitle')
    def subheader(self):
        return  self.subtitle

    def panel(self):
        logo  = """<a href="http://panel.pyviz.org">
                <img src="https://panel.pyviz.org/_static/logo_stacked.png" 
                    width=200 height=150 align="center" margin=20px>"""
        self.get_data()

        return pn.Row(
            pn.Column(logo,self.date_slider),  
            pn.Column(self.header,self.subheader,self.arima_model))

panel_class().panel().servable()

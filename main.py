
import datetime
from os.path import dirname, join

import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.palettes import Blues4
from bokeh.plotting import figure

STATISTICS = ['Total Cases', 'Total Deaths', 'Total Recovered', 'New Cases', 'New Deaths', 'New Recovered']

def get_dataset(src, name, distribution):

    df = src[src.Island == name].copy()
    del df['Island']
    df['Date'] = pd.to_datetime(df.date)
    # timedelta here instead of pd.DateOffset to avoid pandas bug < 0.18 (Pandas issue #11925)
    df['left'] = df.date - datetime.timedelta(days=0.5)
    df['right'] = df.date + datetime.timedelta(days=0.5)
    df = df.set_index(['Date'])
    df.sort_index(inplace=True)
    if distribution == 'Smoothed':
        window, order = 51, 3
        for key in STATISTICS:
            df[key] = savgol_filter(df[key], window, order)

    return ColumnDataSource(data=df)

def make_plot(source, title):
    plot = figure(x_axis_type="datetime", width=800, tools="", toolbar_location=None)
    plot.title.text = title

    plot.quad(top='Total Cases', bottom='New Cases', left='left', right='right',
              color=Blues4[2], source=source, legend_label="Cases")
    plot.quad(top='Total Deaths', bottom='New Deaths', left='left', right='right',
              color=Blues4[1], source=source, legend_label="Deaths")
    plot.quad(top='Total Recovered', bottom='New Recovered', left='left', right='right',
              color=Blues4[0], alpha=0.5, line_color="black", source=source, legend_label="Recovered")

    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Total"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.grid.grid_line_alpha = 0.3

    return plot

def update_plot(attrname, old, new):
    island = island_select.value
    plot.title.text = "Weather data for " + island[pulau]['title']

    src = get_dataset(df, island[pulau]['Island'], distribution_select.value)
    source.data.update(src.data)

pulau = 'Jawa'
distribution = 'Discrete'

island = {
    'Jawa': {
        'Island': 'Jawa',
        'title': 'Jawa',
    },
    'Sumatera': {
        'Island': 'Sumatera',
        'title': 'Sumatera',
    },
    'Kalimantan': {
        'Island': 'Kalimantan',
        'title': 'Kalimantan',
    },
    'Papua': {
        'Island': 'Papua',
        'title': 'Papua',
    }
}

island_select = Select(value=pulau, title='pulau', options=sorted(island.keys()))
distribution_select = Select(value=distribution, title='Distribution', options=['Discrete', 'Smoothed'])

df = pd.read_csv(join(dirname(__file__), 'data/covid.csv'))
source = get_dataset(df, island[pulau]['Island'], distribution)
plot = make_plot(source, "Covid cases for " + island[pulau]['title'])

island_select.on_change('value', update_plot)
distribution_select.on_change('value', update_plot)

controls = column(island_select, distribution_select)

curdoc().add_root(row(plot, controls))
curdoc().title = "Covid Cases"
import datetime
from os.path import dirname, join

import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import BoxSelectTool
from bokeh.models import Slider, CustomJS, Range1d
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.palettes import Blues4
from bokeh.plotting import figure

STATISTICS = ['Total Cases', 'Total Deaths', 'Total Recovered', 'New Cases', 'New Deaths', 'New Recovered']

def get_dataset(src, name, distribution):

    df = src[src.Island == name].copy()
    #del df
    df['Date'] = pd.to_datetime(df.Date)
    # timedelta here instead of pd.DateOffset to avoid pandas bug < 0.18 (Pandas issue #11925)
    df['left'] = df.Date - datetime.timedelta(days=0.5)
    df['right'] = df.Date + datetime.timedelta(days=0.5)
    df = df.set_index(['Date'])
    df.sort_index(inplace=True)
    if distribution == 'Smoothed':
        window, order = 51, 3
        for key in STATISTICS:
            df[key] = savgol_filter(df[key], window, order)
    return ColumnDataSource(data=df)

def make_plot(source, title):
    plot = figure(background_fill_color = '#efefef', x_axis_type="datetime", width=800, y_range = Range1d(start = 0, end = 10000), tools="pan,wheel_zoom,box_zoom,reset", toolbar_location='above')
    plot.title.text = title

    plot.line(x='Date', y='New Cases', source=source, legend_label="Cases", line_color="black", color=Blues4[2])
    plot.line(x='Date', y='New Deaths', source=source, legend_label="Deaths",line_color="red", color=Blues4[1])
    plot.line(x='Date', y='New Recovered', source=source, legend_label="Recovered",line_color="green", color=Blues4[0])

    # fixed attributes
    plot.add_tools(BoxSelectTool(dimensions="width"))
    
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Total"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.grid.grid_line_alpha = 0.3

    return plot

def update_plot(attrname, old, new):
    pulau = island_select.value
    plot.title.text = "Covid cases for " + island[pulau]['title']

    src = get_dataset(df, island[pulau]['Island'], distribution_select.value)
    source.data.update(src.data)

def update(attr, old, new):
    global last_value
    if last_value is not None:
        if new > 0:
            if new > last_value:
                plot.y_range.start = plot.y_range.start + new
                plot.y_range.end = plot.y_range.end - new

                plot.x_range.start = plot.x_range.start + new
                plot.x_range.end = plot.x_range.end - new
            else:
                plot.y_range.start = plot.y_range.start - new
                plot.y_range.end = plot.y_range.end + new

                plot.x_range.start = plot.x_range.start - new
                plot.x_range.end = plot.x_range.end + new
        elif new < 0:
            if new < last_value:
                plot.y_range.start = plot.y_range.start + new
                plot.y_range.end = plot.y_range.end - new

                plot.x_range.start = plot.x_range.start + new
                plot.x_range.end = plot.x_range.end - new
            else:
                plot.y_range.start = plot.y_range.start - new
                plot.y_range.end = plot.y_range.end + new

                plot.x_range.start = plot.x_range.start - new
                plot.x_range.end = plot.x_range.end + new

    last_value = new

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

slider_zoom = Slider(title = 'Zoom', start = -400, end = 800, value = 0, step = 100, align='center')
zoom_value = slider_zoom.value
last_value = None

island_select = Select(value=pulau, title='Select Island', options=sorted(island.keys()))
distribution_select = Select(value=distribution, title='Distribution', options=['Discrete', 'Smoothed'])

df = pd.read_csv(join(dirname(__file__), 'data/covid.csv'))
source = get_dataset(df, island[pulau]['Island'], distribution)
plot = make_plot(source, "Covid cases for " + island[pulau]['Island'] + ' Island')

island_select.on_change('value', update_plot)
distribution_select.on_change('value', update_plot)
slider_zoom.on_change('value', update)

controls = column(island_select, distribution_select)

curdoc().add_root(row(plot, controls))
curdoc().add_root(row(slider_zoom))
curdoc().title = "Covid Cases"
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
import numpy as np

source = ColumnDataSource(data=dict(x=[], y=[]))

plot = figure(title="Random Data", x_axis_label='X', y_axis_label='Y')
plot.line('x', 'y', source=source)

def update():
    new_data = dict(x=np.random.random(10), y=np.random.random(10))
    source.stream(new_data)

curdoc().add_periodic_callback(update, 1000)
curdoc().add_root(column(plot))

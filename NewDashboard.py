import logging
import log.utils as mylog

mylog.add_logger(log_level=logging.DEBUG, name='data_client')
mylog.add_logger(log_level=logging.DEBUG, name='KONEPS-Dashboard')

import bokeh_app.common as app
from bokeh.io import curdoc

curdoc().add_root(app.common_layout)
app.reflect_url()
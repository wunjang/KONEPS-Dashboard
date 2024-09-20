from bokeh_app import utils, common
from bokeh_app.search_biz import layout
import bokeh_app.search_bid.layout as bid_layout
import bokeh_app.search_bid.utils as bid_utils
from bokeh.models import CustomJS, Range1d
import data_client.data as data_module
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from bokeh.io import curdoc

# Callback Functions
def search_callback(input_value):
    biz_no = input_value
    fetched_data = data_module.fetch_bidresults_by_biz(biz_no)
    if not fetched_data:
        common.search_status.text = "데이터가 없습니다"
        return
    else:
        common.search_status.text = "검색 완료"

    bid_layout.update_original_data(fetched_data)

    layout.price_range_options = ["예가 범위",] + list(set(str(item[9]) for item in fetched_data))
    layout.price_range_radio.labels = layout.price_range_options
    biz_count_min = min(fetched_data, key=lambda x: x[11])[11]
    biz_count_max = max(fetched_data, key=lambda x: x[11])[11]
    layout.biz_count_range_slider.start = biz_count_min
    layout.biz_count_range_slider.end = biz_count_max
    layout.biz_count_range_slider.value = (biz_count_min, biz_count_max)

def update_plot(attr, old, new):
    df = pd.DataFrame(bid_layout.filtered_table_data.data)
    df = df.sort_values(by='bidDate')
    df = df[['bidNo', 'bidDiff', 'rank', 'bidDate']]

    layout.line_data.data = df
    layout.win_data.data = df[df['rank'] == 1]

    #layout.line_plot.renderers.clear()

def update_date_range_radio(attr, old, new):
    today = datetime.date.today()
    if new == 1:
        layout.date_picker_begin.value = today - relativedelta(months=3)
        layout.date_picker_end.value = today
    elif new == 2:
        layout.date_picker_begin.value = today - relativedelta(months=6)
        layout.date_picker_end.value = today
    elif new == 3:
        layout.date_picker_begin.value = today - relativedelta(years=1)
        layout.date_picker_end.value = today

def apply_filters(attr, old, new):
    biz_count_min, biz_count_max = layout.biz_count_range_slider.value
    filtered_data = bid_utils.filter_data(
        bid_layout.original_table_data.data,
        date_begin=layout.date_picker_begin.value, 
        date_end=layout.date_picker_end.value, 
        price_range=layout.price_range_options[layout.price_range_radio.active], 
        biz_count_min=int(round(biz_count_min)),
        biz_count_max=int(round(biz_count_max)))
    bid_layout.filtered_table_data.data = filtered_data

def reflect_url(params):
    if 'bin_count' in params:
        bid_layout.bin_count_slider.value = int(params['bin_count'][0])
    if 'date_begin' in params:
        layout.date_picker_begin.value = params['date_begin'][0].decode('utf-8')
    if 'date_end' in params:
        layout.date_picker_end.value = params['date_end'][0].decode('utf-8')
    if 'price_range' in params:
        layout.price_range_radio.active = int(params['price_range'][0])
    if 'biz_count_min' in params and 'biz_count_max' in params:
        layout.biz_count_range_slider.value = (
            int(params['biz_count_min'][0]), 
            int(params['biz_count_max'][0])
        ) 

# CustomJS Callbacks
date_begin_url_callback = CustomJS(args=dict(date_picker_begin=layout.date_picker_begin), code="""
    var url = new URL(window.location);
    if (date_picker_begin.value) {
        url.searchParams.set('date_begin', date_picker_begin.value);
    } else {
        url.searchParams.delete('date_begin');
    }
    window.history.pushState({}, '', url);
    """)

date_end_url_callback = CustomJS(args=dict(date_picker_end=layout.date_picker_end), code="""
    var url = new URL(window.location);
    if (date_picker_end.value) {
        url.searchParams.set('date_end', date_picker_end.value);
    } else {
        url.searchParams.delete('date_end');
    }
    window.history.pushState({}, '', url);
    """)

price_range_url_callback = CustomJS(args=dict(price_range_radio=layout.price_range_radio), code="""
    var url = new URL(window.location);
    url.searchParams.set('price_range', price_range_radio.active);
    window.history.pushState({}, '', url);
    """)

biz_count_url_callback = CustomJS(args=dict(biz_count_range_slider=layout.biz_count_range_slider), code="""
    var url = new URL(window.location);
    url.searchParams.set('biz_count_min', parseInt(biz_count_range_slider.value[0]));
    url.searchParams.set('biz_count_max', parseInt(biz_count_range_slider.value[1]));
    window.history.pushState({}, '', url);
    """)

# Add Callback Functions
layout.date_range_radio.on_change('active', update_date_range_radio)
layout.date_picker_begin.js_on_change('value', date_begin_url_callback)
layout.date_picker_begin.on_change('value', apply_filters)
layout.date_picker_end.js_on_change('value', date_end_url_callback)
layout.date_picker_end.on_change('value', apply_filters)
layout.price_range_radio.on_change('active', apply_filters)
layout.price_range_radio.js_on_change('active', price_range_url_callback)
layout.biz_count_range_slider.on_change('value_throttled', apply_filters)
layout.biz_count_range_slider.js_on_change('value_throttled', biz_count_url_callback)
bid_layout.filtered_table_data.on_change('data', update_plot)
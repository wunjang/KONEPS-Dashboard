from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, DataRange1d,
    TextInput, Button, DataTable, TableColumn, Div,
    NumberFormatter, StringFormatter, DateFormatter, RadioButtonGroup, Range1d,
    DatePicker, Dropdown, Slider, RangeSlider, Paragraph, CustomJS, HTMLTemplateFormatter
)
from bokeh.layouts import column, row
from bokeh_app import utils
import pandas as pd

import bokeh_app.search_bid.layout as bid

line_plot = figure(title="과거 사정율 사용 이력", x_axis_type='datetime', background_fill_color="#fafafa")

line_plot.x_range = DataRange1d()
line_plot.y_range = Range1d(start=0.7, end=1.3)

line_data = ColumnDataSource(data=dict(bidNo=[], bidDiff=[], rank=[], bidDate=[]))
line_plot.line('bidDate', 'bidDiff', source=line_data, line_width=2, color='blue')

win_data = ColumnDataSource(data=dict(bidNo=[], bidDiff=[], rank=[], bidDate=[]))
line_plot.scatter('bidDate', 'bidDiff', size=8, source=win_data, color='red', legend_label='1위 입찰', fill_alpha=0.6, line_color=None)

line_hover = HoverTool()
line_hover.tooltips = [
    ("공고번호", "@bidNo"),
    ("사정율", "@bidDiff"),
    ("순위", "@rank")
]
line_hover.attachment = "horizontal"

line_plot.add_tools(line_hover)

date_picker_begin = DatePicker(title="시작일")
date_picker_end = DatePicker(title="종료일")

date_range_options = ["선택", "최근 3개월", "최근 6개월", "최근 1년"]
date_range_radio = RadioButtonGroup(labels=date_range_options, active=0)

price_range_options = ["예가 범위",]
price_range_radio = RadioButtonGroup(labels=price_range_options, active=0)

biz_count_range_slider = RangeSlider(title="참여업체 수", start=0, end=1, step=1, value=(0,1))

reset_filter_button = Button(label='초기화', button_type='warning')

def update_original_data(data_list):
    bid.update_original_data(data_list)

layout = column(
    row(column(bid.bar_plot, bid.bin_count_slider), line_plot),
    row(date_picker_begin, date_picker_end, date_range_radio, reset_filter_button),
    row(price_range_radio, biz_count_range_slider),
    bid.data_table
)
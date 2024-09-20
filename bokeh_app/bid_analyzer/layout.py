from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, DataRange1d,
    TextInput, Button, DataTable, TableColumn, Div,
    NumberFormatter, StringFormatter, DateFormatter, RadioButtonGroup, Range1d,
    DatePicker, Dropdown, Slider, RangeSlider, Paragraph, CustomJS, HTMLTemplateFormatter
)
from bokeh.layouts import column, row
import data_client.data as data_module
from collections import defaultdict
from bokeh_app import utils

# Plot
color_mapper = LinearColorMapper(palette="Viridis256")
plot_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[]))
line_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[]))
plot = figure(title="사정율 구간별 낙찰 확률 예측", background_fill_color="#fafafa")
plot.quad(top='top', bottom=0, left='left', right='right', source=plot_data, fill_color={'field':'top', 'transform': color_mapper}, line_color='line_color', line_width='line_width', alpha=0.7)
plot.line('bidDiff', 'win_chance', source=line_data, line_width=2, color='black')
plot.x_range = DataRange1d()
plot.y_range = DataRange1d()

# DataTable
columns = [
    TableColumn(field="bizNo", title="사업자번호", formatter=StringFormatter()),
    TableColumn(field="bizName", title="업체명", formatter=StringFormatter()),
    TableColumn(field="bizOwner", title="대표명", formatter=StringFormatter()),
    TableColumn(field="rank_mean", title="평균순위", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="count", title="참여횟수", formatter=NumberFormatter(format="0,0")),
    TableColumn(field="bidDiff_mean", title="평균사정율", formatter=NumberFormatter(format="0.0000")),
    TableColumn(field="bidDiff_variance", title="사정율분산", formatter=NumberFormatter(format="0.0000")),
    TableColumn(field="bidDiff_expectation", title="예상사정율", formatter=NumberFormatter(format="0.0000"))
]

table_data = ColumnDataSource(data=dict(bizNo=[], bizName=[], bizOwner=[], rank_mean=[], count=[], bidDiff_mean=[], bidDiff_variance=[], bidDiff_expectation=[]))
data_table = DataTable(source=table_data, columns=columns, width=900, height=900)

# Layout
layout = column(
    plot,
    data_table
)

def update_datatable(biz_data):
    table_data.data = {
        'bizNo': list(biz_data.keys()),
        'bizName': [biz_data[bizNo]['bizName'] for bizNo in biz_data],
        'bizOwner': [biz_data[bizNo]['bizOwner'] for bizNo in biz_data],
        'rank_mean': [float(biz_data[bizNo]['rank_mean']) for bizNo in biz_data],
        'count': [biz_data[bizNo]['count'] for bizNo in biz_data],
        'bidDiff_mean': [float(biz_data[bizNo]['bidDiff_mean']) for bizNo in biz_data],
        'bidDiff_variance': [float(biz_data[bizNo]['bidDiff_variance']) for bizNo in biz_data],
        # TODO. bidDiff_expectation의 적절한 계산 필요
        'bidDiff_expectation': [float(biz_data[bizNo]['bidDiff_mean']) for bizNo in biz_data]
    }
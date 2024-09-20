from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, DataRange1d,
    TextInput, Button, DataTable, TableColumn, Div,
    NumberFormatter, StringFormatter, DateFormatter, RadioButtonGroup, Range1d,
    DatePicker, Dropdown, Slider, RangeSlider, Paragraph, CustomJS, HTMLTemplateFormatter
)
from bokeh.layouts import column
from bokeh_app import utils
from datetime import date

color_mapper = LinearColorMapper(palette="Viridis256")

bar_data = ColumnDataSource(data=dict(top=[], left=[], right=[], biz_names=[], line_color=[], line_width=[]))
bar_plot = figure(title="구간별 사정율 사용 횟수", background_fill_color="#fafafa")
bar_plot.quad(top='top', bottom=0, left='left', right='right', source=bar_data, fill_color={'field':'top', 'transform': color_mapper}, line_color='line_color', line_width='line_width', alpha=0.7)

bar_plot.x_range = Range1d(0.7, 1.3)
bar_plot.y_range = Range1d(0, 10)

bar_hover = HoverTool()
bar_hover.tooltips = [
    ("범위", "@left{0.0000} - @right{0.0000}"),
    ("값", "@top"),
    ("업체명", """
        <div style="width: 400px; word-wrap: white-space: normal;">
            @biz_names{safe}
        </div>
    """)
]
bar_plot.add_tools(bar_hover)

bin_count_slider = Slider(title="구간 갯수", start=1, end=120, value = 60, width=bar_plot.width)

bid_no_search_formatter = HTMLTemplateFormatter(template=f"""
    <a href="{utils.base_url}?search_option=0&search_input=<%= value %>" target="_blank"><%= value %></a>
""")
biz_no_search_formatter = HTMLTemplateFormatter(template=f"""
    <a href="{utils.base_url}?search_option=1&search_input=<%= value %>" target="_blank"><%= value %></a>
""")
columns = [
    TableColumn(field="bidNo", title="공고번호", formatter=bid_no_search_formatter),
    TableColumn(field="bizName", title="업체명", formatter=StringFormatter(), width=200),
    TableColumn(field="bizOwner", title="대표명", formatter=StringFormatter(), width=100),
    TableColumn(field="bizNo", title="사업자번호", formatter=biz_no_search_formatter),
    TableColumn(field="rank", title="순위", formatter=StringFormatter(), width=50),
    TableColumn(field="bidPrice", title="입찰액(원)", formatter=NumberFormatter()),
    TableColumn(field="bidRatio", title="투찰율", formatter=NumberFormatter(format="0.000"), width=150),
    TableColumn(field="bidDiff", title="사정율", formatter=NumberFormatter(format="0.0000"), width=150),
    TableColumn(field="priceRange", title="예가범위", formatter=NumberFormatter(), width=100),
    TableColumn(field="bidDate", title="공고일자", formatter=DateFormatter(format="%Y-%m-%d")),
    TableColumn(field="biz_count", title="참여업체", formatter=NumberFormatter(), width=100),
]

original_table_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[], biz_count=[]))
filtered_table_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[], biz_count=[]))
data_table = DataTable(source=filtered_table_data, columns=columns, width=900, height=900)

def _update_source(source, data):
    source.data = {
        'bidNo': [item[1] for item in data],
        'bizName': [item[2] for item in data],
        'bizOwner': [item[3] for item in data],
        'bizNo': [item[4] for item in data],
        'rank': [item[5] for item in data],
        'bidPrice': [item[6] for item in data],
        'bidRatio': [float(item[7]) for item in data],
        'bidDiff': [float(item[8]) for item in data],
        'priceRange': [int(item[9]) for item in data],
        'bidDate': [item[10] for item in data],
        'biz_count': [int(item[11]) for item in data]
    }
    
def update_original_data(data):
    _update_source(original_table_data, data)
    _update_source(filtered_table_data, data)

def update_data(data):
    _update_source(filtered_table_data, data)



layout = column(
    bar_plot,
    bin_count_slider,
    data_table
)
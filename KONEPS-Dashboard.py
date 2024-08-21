import Data.data as data_module
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, ColorBar, TextInput, Button, DataTable, TableColumn, NumberFormatter, StringFormatter, DateFormatter, RadioButtonGroup, Range1d, WheelZoomTool, BoxZoomTool, ResetTool
from bokeh.layouts import column, row
import numpy as np

def search_callback():
    input_value = input_field.value.rstrip()
    if not input_value:
        return
    
    selected_option = search_options[radio_button_group.active]
    if selected_option == "공고번호":
        line_plot.visible = False
        update_barplot(data_module.fetch_bidresults_by_bid(input_value))
    elif selected_option == "사업자번호":
        line_plot.visible = True
        update_barplot(data_module.fetch_bidresults_by_biz(input_value))
        update_lineplot(data_module.fetch_bidresults_by_biz(input_value))

def update_lineplot(data_list):
    """공고번호에 따라 데이터를 정렬하여 꺾은선 그래프를 그립니다"""
    update_datatable(data_list)

    sorted_data = sorted(data_list, key=lambda x: x[10])  # 공고일자로 정렬
    
    #line_plot.x_range[sorted_data[1]]

    #rank_1_source = ColumnDataSource(sorted_data[sorted_data[5] == 1])
    #line_plot.circle('bidno', 'biddiff', size=8, source=rank_1_source, color='red', legend_label='Bidrank 1', fill_alpha=0.6, line_color=None)

    line_plot.y_range = Range1d(start=0.7, end=1.3)
    print(type(sorted_data[0][10]))
    line_data.data = {
        'bidNo': [item[1] for item in sorted_data],
        'bidDiff': [float(item[8]) for item in sorted_data],
        'rank': [item[5] for item in sorted_data],
        'bidDate': [pd.to_datetime(item[10]) for item in sorted_data]
    }

    line_plot.renderers.clear()

    # 새로운 라인 추가
    line_plot.line('bidDate', 'bidDiff', source=line_data, line_width=2, color='blue')


def update_barplot(data_list):
    update_datatable(data_list)

    # 데이터 추출 및 필터링
    bid_diff = [float(item[8]) for item in data_list]
    biz_names = [item[2] for item in data_list]  # Assuming bizName is in the second column

    # Filter values within the range 0.97 to 1.03
    filtered_values = [(value, biz_name, item[5] == 1) for value, biz_name, item in zip(bid_diff, biz_names, data_list) if 0.97 <= value <= 1.03]
    filtered_biddiff_values = [fv[0] for fv in filtered_values]
    filtered_biz_names = [fv[1] for fv in filtered_values]
    highlight_flags = [fv[2] for fv in filtered_values]

    # Define bins (adjust the number of bins as needed)
    num_bins = 60
    bins = np.linspace(0.97, 1.03, num_bins + 1)

    # Compute histogram
    hist, edges = np.histogram(filtered_biddiff_values, bins=bins)

    # Prepare biz_names for each bin
    biz_names_for_bins = [[] for _ in range(len(edges)-1)]
    highlight_flags_for_bins = [[] for _ in range(len(edges)-1)]
    for value, biz_name, highlight_flag in zip(filtered_biddiff_values, filtered_biz_names, highlight_flags):
        for i in range(len(edges)-1):
            if edges[i] <= value < edges[i+1]:
                display_name = f'{biz_name} ({value:.3f})'
                biz_names_for_bins[i].append(f'<span style="color:red;">{display_name}</span>' if highlight_flag else display_name)
                highlight_flags_for_bins[i].append(highlight_flag)

    # Convert biz_names lists to strings
    biz_names_strings = [" / ".join(names) for names in biz_names_for_bins]

    # Determine line colors and widths
    line_colors = ['red' if any(flags) else 'white' for flags in highlight_flags_for_bins]
    line_widths = [2 if any(flags) else 1 for flags in highlight_flags_for_bins]

    # Prepare data for Bokeh
    source.data = dict(
        top=hist,
        left=edges[:-1],
        right=edges[1:],
        biz_names=biz_names_strings,
        line_color=line_colors,
        line_width=line_widths
    )

# Bokeh 레이아웃 구성 요소
input_field = TextInput(value="", title="Enter Bid Number:")
submit_button = Button(label="검색", button_type="success")

submit_button.on_click(search_callback)

search_options = ["공고번호", "사업자번호"]
radio_button_group = RadioButtonGroup(labels=search_options, active = 0)

# Color mapper for bar colors
color_mapper = LinearColorMapper(palette="Viridis256")

# Initial plots
source = ColumnDataSource(data=dict(top=[], left=[], right=[], biz_names=[], line_color=[], line_width=[]))
bar_plot = figure(title="사정율 구간별 등장 횟수", tools="", background_fill_color="#fafafa", x_range=(0.97, 1.03))
bar_plot.quad(top='top', bottom=0, left='left', right='right', source=source, fill_color={'field':'top', 'transform': color_mapper}, line_color='line_color', line_width='line_width', alpha=0.7)
bar_plot.min_border = 75

line_data = ColumnDataSource(data=dict(bidNo=[], bidDiff=[], rank=[], bidDate=[]))
line_plot = figure(title="과거 사정율 사용 기록", tools="", x_axis_type='datetime', background_fill_color="#fafafa")
line_plot.line('bidDate', 'bidDiff', source=line_data, line_width=2, color='blue')

line_plot.x_range.start = pd.to_datetime('2023-01-01')
line_plot.x_range.end = pd.to_datetime('2023-12-31')
line_plot.y_range.start = 0
line_plot.y_range.end = 10

# Add tools
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

line_hover = HoverTool()
line_hover.tooltips = [
    ("공고번호", "@bidNo"),
    ("사정율", "@bidDiff"),
    ("순위", "@rank")
]
line_hover.attachment = "horizontal"

line_plot.add_tools(line_hover)
line_plot.add_tools(BoxZoomTool(), ResetTool())

wheel_zoom = WheelZoomTool()
#bar_plot.add_tools(wheel_zoom)
#bar_plot.toolbar.active_scroll = wheel_zoom
#bar_plot.toolbar.active_scroll.axis = 'x'

# DataTable 구성
columns = [
    TableColumn(field="bidNo", title="공고번호", formatter=StringFormatter()),
    TableColumn(field="bizName", title="업체명", formatter=StringFormatter()),
    TableColumn(field="bizOwner", title="대표명", formatter=StringFormatter(), width=100),
    TableColumn(field="bizNo", title="사업자번호", formatter=StringFormatter()),
    TableColumn(field="rank", title="순위", formatter=StringFormatter(), width=50),
    TableColumn(field="bidPrice", title="입찰액(원)", formatter=NumberFormatter(format="0,0")),
    TableColumn(field="bidRatio", title="투찰율", formatter=NumberFormatter(format="0.000"), width=150),
    TableColumn(field="bidDiff", title="사정율", formatter=NumberFormatter(format="0.0000"), width=150),
    TableColumn(field="priceRange", title="예가범위", formatter=StringFormatter(), width=100),
    TableColumn(field="bidDate", title="공고일자", formatter=DateFormatter(format="%Y-%m-%d")),
]

table_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[]))
data_table = DataTable(source=table_data, columns=columns, width=900)

def update_datatable(data_list):
    # Update data table
    table_data.data = {
        'bidNo': [item[1] for item in data_list],
        'bizName': [item[2] for item in data_list],
        'bizOwner': [item[3] for item in data_list],
        'bizNo': [item[4] for item in data_list],
        'rank': [item[5] for item in data_list],
        'bidPrice': [item[6] for item in data_list],
        'bidRatio': [float(item[7]) for item in data_list],
        'bidDiff': [float(item[8]) for item in data_list],
        'priceRange': [item[9] for item in data_list],
        'bidDate': [pd.to_datetime(item[10]) for item in data_list],
    }

# Layout
line_plot.visible = False
layout = column(radio_button_group, row(input_field, submit_button), row(bar_plot, line_plot), data_table)

# Bokeh 서버에 레이아웃 추가
curdoc().add_root(layout)

import Data.data as data_module
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, ColorBar, TextInput, Button, DataTable, TableColumn, NumberFormatter, StringFormatter
from bokeh.layouts import column, row
import numpy as np

def update_plot():
    bid_no = bid_no_input.value
    if not bid_no:
        return

    data_list = data_module.GetBidResultsByBidNo(bid_no)

    # Update data table
    table_data.data = {
        '공고번호': [item[1] for item in data_list],
        '업체명': [item[2] for item in data_list],
        '대표명': [item[3] for item in data_list],
        '사업자번호': [item[4] for item in data_list],
        '순위': [item[5] for item in data_list],
        '입찰액': [item[6] for item in data_list],
        '투찰율': [float(item[7]) for item in data_list],
        '사정율': [float(item[8]) for item in data_list]
    }

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
bid_no_input = TextInput(value="", title="Enter Bid Number:")
submit_button = Button(label="Show Bid Results", button_type="success")

submit_button.on_click(update_plot)

# Color mapper for bar colors
color_mapper = LinearColorMapper(palette="Viridis256")

# Initial empty plot
source = ColumnDataSource(data=dict(top=[], left=[], right=[], biz_names=[], line_color=[], line_width=[]))
p = figure(title="Bar Chart of Values with bizName Tooltips", tools="", background_fill_color="#fafafa", x_range=(0.96, 1.04))
p.quad(top='top', bottom=0, left='left', right='right', source=source, fill_color={'field':'top', 'transform': color_mapper}, line_color='line_color', line_width='line_width', alpha=0.7)

# Add tooltips
hover = HoverTool()
hover.tooltips = [
    ("Value", "@left{0.000} - @right{0.000}"),
    ("Frequency", "@top"),
    ("bizName", "@biz_names{safe}")
]
p.add_tools(hover)

# DataTable 구성
columns = [
    TableColumn(field="공고번호", title="공고번호", formatter=StringFormatter()),
    TableColumn(field="업체명", title="업체명", formatter=StringFormatter()),
    TableColumn(field="대표명", title="대표명", formatter=StringFormatter()),
    TableColumn(field="사업자번호", title="사업자번호", formatter=NumberFormatter()),
    TableColumn(field="순위", title="순위", formatter=StringFormatter()),
    TableColumn(field="입찰액", title="입찰액", formatter=NumberFormatter(format="0,0")),
    TableColumn(field="투찰율", title="투찰율", formatter=NumberFormatter(format="0.0000")),
    TableColumn(field="사정율", title="사정율", formatter=NumberFormatter(format="0.0000")),
]

table_data = ColumnDataSource(data=dict(공고번호=[], 업체명=[], 대표명=[], 사업자번호=[], 순위=[], 입찰액=[], 투찰율=[], 사정율=[]))
data_table = DataTable(source=table_data, columns=columns, width=800)

# Layout
layout = column(bid_no_input, submit_button, p, data_table)

# Bokeh 서버에 레이아웃 추가
curdoc().add_root(layout)

import Data.data as data_module
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, DataRange1d,
    TextInput, Button, DataTable, TableColumn, Div,
    NumberFormatter, StringFormatter, DateFormatter, RadioButtonGroup, Range1d,
    DatePicker, Dropdown, Slider, RangeSlider, Paragraph, CustomJS
)
from bokeh.models.tools import WheelZoomTool, BoxZoomTool, ResetTool, PanTool
from bokeh.layouts import column, row
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta

fetched_data = None
def search_callback():
    input_value = search_input_field.value.rstrip()
    if not input_value:
        return

    global fetched_data
    selected_option = search_options[search_radio.active]
    print(f"search: {input_value}, option: {selected_option}")
    if selected_option == "공고번호":
        fetched_data = data_module.fetch_bidresults_by_bid(input_value)
        if not fetched_data:
            search_alert_paragraph.visible = True
            return
        else:
            search_alert_paragraph.visible = False

        update_barplot(fetched_data)
        update_datatable(fetched_data)

    elif selected_option == "사업자번호":
        fetched_data = data_module.fetch_bidresults_by_biz(input_value)
        if not fetched_data:
            search_alert_paragraph.visible = True
            return
        else:
            search_alert_paragraph.visible = False

        update_barplot(fetched_data)
        update_lineplot(fetched_data)
        update_datatable(fetched_data)

        # setup filters
        bin_count_slider.value = 60 # default

        # setup bidresults filters
        global price_range_options
        price_range_options = ["예가 범위",] + list(set(str(item[9]) for item in fetched_data))
        price_range_radio.labels = price_range_options
        biz_count_min = min(fetched_data, key=lambda x: x[11])[11]
        biz_count_max = max(fetched_data, key=lambda x: x[11])[11]
        biz_count_range_slider.start = biz_count_min
        biz_count_range_slider.end = biz_count_max
        biz_count_range_slider.value = (biz_count_min, biz_count_max)

        reset_bidresult_filter()

def update_lineplot(data_list):
    """공고번호에 따라 데이터를 정렬하여 꺾은선 그래프를 그립니다"""
    if not data_list:
        return
    sorted_data = sorted(data_list, key=lambda x: x[10])  # 공고일자로 정렬

    line_plot.y_range = Range1d(start=0.7, end=1.3)
    line_plot.x_range = DataRange1d()
    line_data.data = {
        'bidNo': [item[1] for item in sorted_data],
        'bidDiff': [float(item[8]) for item in sorted_data],
        'rank': [item[5] for item in sorted_data],
        'bidDate': [pd.to_datetime(item[10]) for item in sorted_data]
    }

    line_plot.renderers.clear()

    # 새로운 라인 추가
    line_plot.line('bidDate', 'bidDiff', source=line_data, line_width=2, color='blue')
    df = pd.DataFrame(line_data.data)

    # rank가 1인 데이터만 필터링
    filtered_df = df[df['rank'] == 1]

    # 다시 line_data.data에 필터링된 데이터를 할당
    rank_1_source = ColumnDataSource(data=filtered_df.to_dict(orient='list'))
    line_plot.scatter('bidDate', 'bidDiff', size=8, source=rank_1_source, color='red', legend_label='1위 입찰', fill_alpha=0.6, line_color=None)

    

def update_barplot(data_list):
    if not data_list:
        return

    # 데이터 추출 및 필터링
    bid_diff_list = [float(item[8]) for item in data_list]
    price_range_max = max(data_list, key=lambda x: x[9])[9]
    price_range_max_min = 1 - price_range_max / 100
    price_range_max_max = 1 + price_range_max / 100
    bar_plot.x_range = Range1d(price_range_max_min, price_range_max_max)

    biz_names = [item[2] for item in data_list]  # Assuming bizName is in the second column

    # Filter values within the range
    filtered_values = [(value, biz_name, item[5] == 1) for value, biz_name, item in zip(bid_diff_list, biz_names, data_list) if price_range_max_min <= value <= price_range_max_max]
    filtered_biddiff_values = [fv[0] for fv in filtered_values]
    filtered_biz_names = [fv[1] for fv in filtered_values]
    highlight_flags = [fv[2] for fv in filtered_values]

    # Define bins (adjust the number of bins as needed)
    num_bins = bin_count_slider.value
    bins = np.linspace(price_range_max_min, price_range_max_max, num_bins + 1)

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
    bar_data.data = dict(
        top=hist,
        left=edges[:-1],
        right=edges[1:],
        biz_names=biz_names_strings,
        line_color=line_colors,
        line_width=line_widths
    )

# Bokeh 레이아웃 구성 요소
search_input_field = TextInput(value="")
search_input_field.on_event('value_submit', search_callback)

search_button = Button(label="검색", button_type="success")
search_button.on_click(search_callback)

search_options = ["공고번호", "사업자번호"]
search_radio = RadioButtonGroup(labels=search_options, active = 1)

search_alert_paragraph = Paragraph(text="데이터가 없습니다.")
search_alert_paragraph.visible = False

def update_search_radio(attr, old, new):
    if new == 0:
        show_biz_search_options(False)
    if new == 1:
        show_biz_search_options(True)

search_radio.on_change('active', update_search_radio)

# Color mapper for bar colors
color_mapper = LinearColorMapper(palette="Viridis256")

# Initial plots
bar_data = ColumnDataSource(data=dict(top=[], left=[], right=[], biz_names=[], line_color=[], line_width=[]))
bar_plot = figure(title="구간별 사정율 사용 횟수", tools="", background_fill_color="#fafafa")
bar_plot.quad(top='top', bottom=0, left='left', right='right', source=bar_data, fill_color={'field':'top', 'transform': color_mapper}, line_color='line_color', line_width='line_width', alpha=0.7)
#bar_plot.min_border = 75

bar_plot.x_range = DataRange1d()
bar_plot.y_range = DataRange1d()

line_data = ColumnDataSource(data=dict(bidNo=[], bidDiff=[], rank=[], bidDate=[]))
line_plot = figure(title="과거 사정율 사용 이력", tools="", x_axis_type='datetime', background_fill_color="#fafafa")
line_plot.line('bidDate', 'bidDiff', source=line_data, line_width=2, color='black')

line_plot.x_range = DataRange1d()
line_plot.y_range = DataRange1d()

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
line_plot.add_tools(BoxZoomTool(), PanTool(), ResetTool())

wheel_zoom = WheelZoomTool()
#bar_plot.add_tools(wheel_zoom)
#bar_plot.toolbar.active_scroll = wheel_zoom
#bar_plot.toolbar.active_scroll.axis = 'x'

bin_count_slider = Slider(title="구간 갯수", start=1, end=120, value = 60, width=bar_plot.width)

date_picker_begin = DatePicker(title="시작일")
date_picker_end = DatePicker(title="종료일")

date_range_options = ["선택", "최근 3개월", "최근 6개월", "최근 1년"]
date_range_radio = RadioButtonGroup(labels=date_range_options, active=0)

def update_date_range_radio(attr, old, new):
    today = datetime.date.today()
    if new == 1:
        date_picker_begin.value = today - relativedelta(months=3)
        date_picker_end.value = today
    elif new == 2:
        date_picker_begin.value = today - relativedelta(months=6)
        date_picker_end.value = today
    elif new == 3:
        date_picker_begin.value = today - relativedelta(years=1)
        date_picker_end.value = today

date_range_radio.on_change('active', update_date_range_radio)

price_range_selected = None
price_range_options = ["예가 범위",]
price_range_radio = RadioButtonGroup(labels=price_range_options, active=0)


biz_count_range_slider = RangeSlider(title="참여업체 수", start=0, end=1, step=1, value=(0,1))

def apply_bidresult_filter():
    global fetched_data, price_range_selected
    biz_count_min, biz_count_max = biz_count_range_slider.value
    filterd_data = data_module.filter_bidresults(
        data_list=fetched_data, 
        date_begin=date_picker_begin.value, 
        date_end=date_picker_end.value, 
        price_range=price_range_selected, 
        biz_count_min=biz_count_min,
        biz_count_max=biz_count_max)
    
    update_barplot(filterd_data)
    update_lineplot(filterd_data)
    update_datatable(filterd_data)

def apply_bidresult_filter_callback(attr, old, new):
    apply_bidresult_filter()

def price_range_radio_callback(attr, old, new):
    global price_range_selected, price_range_options
    if price_range_options[new].isdigit():
        price_range_selected = int(price_range_options[new])
    else:
        price_range_selected = None
    apply_bidresult_filter()


price_range_radio.on_change('active', price_range_radio_callback)
bin_count_slider.on_change('value_throttled', apply_bidresult_filter_callback)

def reset_bidresult_filter():
    global price_range_selected
    biz_count_range_slider.value = (biz_count_range_slider.start, biz_count_range_slider.end)
    price_range_radio.active = 0
    price_range_selected = None
    date_picker_begin.value = None
    date_picker_end.value = None
    date_range_radio.active = 0

    apply_bidresult_filter()


    
apply_filter_button = Button(label='적용', button_type='success')
apply_filter_button.on_click(apply_bidresult_filter)

reset_filter_button = Button(label='초기화', button_type='warning')
reset_filter_button.on_click(reset_bidresult_filter)

# DataTable 구성
columns = [
    TableColumn(field="bidNo", title="공고번호", formatter=StringFormatter()),
    TableColumn(field="bizName", title="업체명", formatter=StringFormatter(), width=200),
    TableColumn(field="bizOwner", title="대표명", formatter=StringFormatter(), width=100),
    TableColumn(field="bizNo", title="사업자번호", formatter=StringFormatter()),
    TableColumn(field="rank", title="순위", formatter=StringFormatter(), width=50),
    TableColumn(field="bidPrice", title="입찰액(원)", formatter=NumberFormatter(format="0,0")),
    TableColumn(field="bidRatio", title="투찰율", formatter=NumberFormatter(format="0.000"), width=150),
    TableColumn(field="bidDiff", title="사정율", formatter=NumberFormatter(format="0.0000"), width=150),
    TableColumn(field="priceRange", title="예가범위", formatter=StringFormatter(), width=100),
    TableColumn(field="bidDate", title="공고일자", formatter=DateFormatter(format="%Y-%m-%d")),
    TableColumn(field="biz_count", title="참여업체", formatter=NumberFormatter(), width=100),
]

table_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[]))
data_table = DataTable(source=table_data, columns=columns, width=900, height=900)

# 우클릭 시 정보를 표시할 Div 생성
output = Div(text="hmm...", width=400, height=100)

# CustomJS 콜백
callback = CustomJS(args=dict(source=table_data, output_div=output), code="""
    console.log(source.selected.indices)
    output.text = source.selected.indices
""")

# DataTable과 콜백 연결
table_data.selected.js_on_change('indices', callback)

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
        'biz_count': [item[11] for item in data_list]
    }

def show_biz_search_options(visible):
    biz_search_options = [line_plot, date_picker_begin, date_picker_end, date_range_radio, price_range_radio, biz_count_range_slider, apply_filter_button, reset_filter_button]
    for item in biz_search_options:
        item.visible = visible

# Layout
layout = column(
    search_radio, 
    row(search_input_field, search_button, search_alert_paragraph), 
    row(column(bar_plot, bin_count_slider), line_plot), 
    row(date_picker_begin, date_picker_end, date_range_radio, apply_filter_button, reset_filter_button),
    row(price_range_radio, biz_count_range_slider),
    output,
    data_table)

# initial setting
show_biz_search_options(True)

# Bokeh 서버에 레이아웃 추가
curdoc().add_root(layout)

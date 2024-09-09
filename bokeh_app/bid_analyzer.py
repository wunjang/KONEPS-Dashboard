from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, DataRange1d,
    TextInput, Button, DataTable, TableColumn, Div,
    NumberFormatter, StringFormatter, DateFormatter, RadioButtonGroup, Range1d,
    DatePicker, Dropdown, Slider, RangeSlider, Paragraph, CustomJS, HTMLTemplateFormatter
)
import data_client.data as data_module
from collections import defaultdict

def setup():
    # 

    # Plot
    color_mapper = LinearColorMapper(palette="Viridis256")
    plot_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[]))
    line_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[]))
    plot = figure(title="사정율 구간별 낙찰 확률 예측", tools="", background_fill_color="#fafafa")
    plot.quad(top='top', bottom=0, left='left', right='right', source=plot_data, fill_color={'field':'top', 'transform': color_mapper}, line_color='line_color', line_width='line_width', alpha=0.7)
    plot.line('bidDiff', 'win_chance', source=line_data, line_width=2, color='black')
    plot.x_range = (0.7, 1.3)
    plot.y_range = (0, 1)

    # DataTable
    columns = [
        TableColumn(field="bizName", title="업체명", formatter=StringFormatter()),
        TableColumn(field="bizOwner", title="대표명", formatter=StringFormatter()),
        TableColumn(field="bizNo", title="사업자번호", formatter=StringFormatter()),
        TableColumn(field="mean_rank", title="평균순위", formatter=StringFormatter()),
        TableColumn(field="attend_count", title="참여횟수", formatter=NumberFormatter(format="0,0")),
        TableColumn(field="mean_bidDiff", title="평균사정율", formatter=NumberFormatter(format="0.0000")),
        TableColumn(field="bidDiff_variance", title="사정율분산", formatter=NumberFormatter(format="0.0000")),
        TableColumn(field="bidDiff_expectation", title="예상사정율", formatter=NumberFormatter(format="0.0000"))
    ]

    table_data = ColumnDataSource(data=dict(bidNo=[], bizName=[], bizOwner=[], bizNo=[], rank=[], bidPrice=[], bidRatio=[], bidDiff=[], priceRange=[], bidDate=[]))
    data_table = DataTable(source=table_data, columns=columns, width=900, height=900)

    # Layout
    layout = columns(
        data_table
    )

    curdoc().add_root(layout)

def bid_analyze(bid_no, biz_region, biz_license):
    """
    Params:
        bid_no(str): 공고번호
        biz_region(str): 사업체가 위치한 지역의 4자리 코드번호
        biz_license(list(str)): 사업체가 보유한 업종 면허 4자리 코드번호의 리스트
    """
    searched_bid = data_module.fetch_bid_by_bid_no(bid_no)
    

def update_biz_data(biz_region, biz_license):
    related_bids = data_module.fetch_bids_by_region_and_license(biz_region, biz_license)
    related_bidnos = [bid[0] for bid in related_bids]
    related_bidresults = data_module.fetch_bidresults_by_bid_list(related_bidnos)
        
    biz_data = defaultdict(lambda: {
        "rank_sum":0,
        "count": 0,
        "bidDiff_sum": 0,
        "squared_diff_sum": 0,
        "bizName": None,
        "bizOwner": None
    })
    for bidresult in related_bidresults:
        biz_data[bidresult[4]]["rank_sum"] += bidresult[5]
        biz_data[bidresult[4]]["count"] += 1
        biz_data[bidresult[4]]["bidDiff_sum"] += bidresult[8]
        if biz_data[bidresult[4]]["bizName"] is None:
            biz_data[bidresult[4]]["bizName"] = bidresult[2]
        if biz_data[bidresult[4]]["bizOwner"] is None:
            biz_data[bidresult[4]]["bizOwner"] = bidresult[3]

    for biz_no in biz_data:
        biz_data[biz_no]["rank_mean"] = biz_data[biz_no]["rank_sum"] / biz_data[biz_no]["count"]
        biz_data[biz_no]["bidDiff_mean"] = biz_data[biz_no]["bidDiff_sum"] / biz_data[biz_no]["count"]

    for bidresult in related_bidresults:
        biz_data[bidresult[4]]["squared_diff_sum"] += (bidresult[8] - biz_data[bidresult[4]]["bidDiff_mean"]) ** 2

    for biz_no in biz_data:
        biz_data[biz_no]["bidDiff_varicance"] = biz_data[biz_no]["squared_diff_sum"] / biz_data[biz_no["count"]]
    
    return biz_data

def update_plot():
    pass

def update_datatable(table_data, biz_data):
    table_data.data = {
        'bizNo': list(biz_data.keys()),
        'bizName': [biz_data[bizNo]['bizName'] for bizNo in biz_data],
        'bizOwner': [biz_data[bizNo]['bizOwner'] for bizNo in biz_data],
        'rank_mean': [biz_data[bizNo]['rank_mean'] for bizNo in biz_data],
        'count': [biz_data[bizNo]['count'] for bizNo in biz_data],
        'bidDiff_mean': [biz_data[bizNo]['bidDiff_mean'] for bizNo in biz_data],
        'bidDiff_variance': [biz_data[bizNo]['bidDiff_variance'] for bizNo in biz_data],
        # TODO. bidDiff_expectation의 적절한 계산 필요
        'bidDiff_expectation': [biz_data[bizNo]['bidDiff_mean'] for bizNo in biz_data]
    }

def update_biz_data_datatalbe(table_data, biz_region, biz_license):
    biz_data = update_biz_data(biz_region, biz_license)
    update_datatable(table_data, biz_data)
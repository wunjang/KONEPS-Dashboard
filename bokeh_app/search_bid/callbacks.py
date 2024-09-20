from bokeh_app import utils, common
from bokeh_app.search_bid import layout
from bokeh.models import CustomJS, Range1d, DataRange1d
import numpy as np

fetched_data = None
# Callback Functions
def search_callback(input_value):
    global fetched_data

    bid_no = input_value
    fetched_data = utils.fetch_or_request_bid_by_bid_no(bid_no)
    if not fetched_data:
        common.search_status.text = "데이터가 없습니다"
        return
    else:
        common.search_status.text = "검색 완료"

    layout.update_data(fetched_data)

def update_plot(attr, old, new):
    data = layout.filtered_table_data.data
    if len(data['priceRange']) == 0:
        return
    
    bar_plot = layout.bar_plot
    bar_data = layout.bar_data
    bin_count_slider = layout.bin_count_slider

    # 데이터 추출 및 필터링
    bid_diff_list = [float(item) for item in data['bidDiff']]
    price_range_max = max(data['priceRange'])
    price_range_max_min = 1 - price_range_max / 100
    price_range_max_max = 1 + price_range_max / 100
    bar_plot.x_range = Range1d(price_range_max_min, price_range_max_max)
    bar_plot.y_range = DataRange1d()

    biz_names = data['bizName']

    # Filter values within the range
    filtered_values = [(value, biz_name, rank == 1) for value, biz_name, rank in zip(bid_diff_list, biz_names, data['rank']) if price_range_max_min <= value <= price_range_max_max]
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

def on_change_bin_count_slider(attr, old, new):
    # TODO. datatable기반으로 그래프를 만들도록 변경
    update_plot(attr, old, new)

# CustomJS Callbacks
bin_count_url_callback = CustomJS(args=dict(bin_count_slider=layout.bin_count_slider), code="""
    var url = new URL(window.location);
    url.searchParams.set('bin_count', parseInt(bin_count_slider.value));
    window.history.pushState({}, '', url);
    """)

# Add Callback Functions
layout.bin_count_slider.on_change('value_throttled', on_change_bin_count_slider)
layout.bin_count_slider.js_on_change('value_throttled', bin_count_url_callback)
layout.filtered_table_data.on_change('data', update_plot)
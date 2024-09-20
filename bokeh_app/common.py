from bokeh.io import curdoc
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, DataRange1d,
    TextInput, Button, DataTable, TableColumn, Div,
    NumberFormatter, StringFormatter, DateFormatter, RadioButtonGroup, Range1d,
    DatePicker, Dropdown, Slider, RangeSlider, Paragraph, CustomJS, HTMLTemplateFormatter
)
from bokeh.layouts import column, row
from .search_bid import layout as search_bid_layout, callbacks as search_bid_callbacks, utils as search_bid_utils
from .search_biz import layout as search_biz_layout, callbacks as search_biz_callbacks, utils as search_biz_utils
from .bid_analyzer import layout as bid_analyzer_layout, callbacks as bid_analyzer_callbacks, utils as bid_analyzer_utils

# Common Layout
search_options = ["공고 검색", "업체 검색", "전략 분석"]
search_radio = RadioButtonGroup(labels=search_options)
search_input = TextInput(value="", name='search_input')
search_button = Button(label="검색", button_type='success')
search_status = Paragraph(text="", name='search_status')

# Common Callback Fucntions
layout_mapping = {
    "공고 검색": search_bid_layout.layout,
    "업체 검색": search_biz_layout.layout,
    "전략 분석": bid_analyzer_layout.layout
}
def on_change_search_radio(attr, old, new):
    selected_option = search_options[new]
    sub_layout = layout_mapping[selected_option]

    layout = column(
        common_layout,
        sub_layout
    )
    curdoc().clear()
    curdoc().add_root(layout)

callback_mapping = {
    "공고 검색": search_bid_callbacks.search_callback,
    "업체 검색": search_biz_callbacks.search_callback,
    "전략 분석": bid_analyzer_callbacks.search_callback
}
def search_callback():
    active = search_radio.active
    if active == None:
        search_status.text = '검색 옵션을 선택해 주세요'
        return
    else:
        search_status.text = ""
    input_value = search_input.value
    selected_option = search_options[active]

    callback_mapping[selected_option](input_value)


# Common CustomJS Callbacks
search_url_callback = CustomJS(args=dict(
    search_radio=search_radio,
    search_input=search_input),
    code="""
    if (!search_input.value || search_input.value.trim() === "") {
        return;
    }

    var url = new URL(window.location);
    url.searchParams.set('search_option', search_radio.active);
    url.searchParams.set('search_input', search_input.value);

    window.history.pushState({}, '', url);
    """)

# Add Callback Functions
search_radio.on_change('active', on_change_search_radio)
search_input.on_event('value_submit', search_callback)
search_input.js_on_event('value_submit', search_url_callback)
search_button.on_click(search_callback)
search_button.js_on_click(search_url_callback)

common_layout = column(
    search_radio,
    row(search_input, search_button, search_status)
)

def reflect_url():
    params = curdoc().session_context.request.arguments
    if 'search_input' in params:
        search_input.value = params['search_input'][0].decode('utf-8')
        search_callback()
    else:
        return
    if 'search_option' in params:
        search_radio.active = int(params['search_option'][0])
        on_change_search_radio(None, None, search_radio.active)
        if search_radio.active == 0:
            search_bid_callbacks.reflect_url(params)
        elif search_radio.active == 1:
            search_biz_callbacks.reflect_url(params)
        elif search_radio.active == 2:
            bid_analyzer_callbacks.reflect_url(params)

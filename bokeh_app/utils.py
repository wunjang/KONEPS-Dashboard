from bokeh.io import curdoc
from urllib.parse import urlparse
from data_client import data as data_module, data_update as update_module



def get_bokeh_object(name:str):
    return next((selected for item in curdoc().roots if (selected := item.select_one(dict(name=name)))), None)

base_url = ""
def extract_base_url():
    global base_url
    request = curdoc().session_context.request
    full_url = f"{request.protocol}://{request.host}{request.uri}"
    parsed_url = urlparse(full_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

def fetch_or_request_bid_by_bid_no(bid_no):
    bid = data_module.fetch_bidresults_by_bid_no(bid_no)
    if not bid:
        update_module.update_bid(bid_no, False)
        bid = data_module.fetch_bidresults_by_bid_no(bid_no)
    return bid


import Data.data as data_module
import Data.public_data_client.data_request as request_module

def update_bids(region:str, industry:str, date_begin:str, date_end:str):
    """
    
    """
    request_module.request_bids_by_region_and_industry(region, industry, date_begin, date_end)
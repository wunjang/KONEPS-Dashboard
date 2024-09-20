import bokeh_app.bid_analyzer.layout as layout
from bokeh_app import common, utils
import data_client.data as data_module

import logging

logger = logging.getLogger('KONEPS-Dashboard')
def datatable_callback():
    pass

def search_callback(input_value):
    bid_counter = 0
    biz_counter = 0

    #region Nested Functions
    def get_biz_data(biz_region, biz_license):
        print(f'지역:{biz_region}, 면허:{biz_license}')
        nonlocal bid_counter, biz_counter
        related_bids = data_module.fetch_bids_by_region_and_license(biz_region, biz_license)
        related_bidnos = [str(bid[0]).strip() for bid in related_bids]
        bid_counter += len(related_bidnos)
        # TODO. 예가 범위 필터링 필요
        related_bidresults = data_module.fetch_bidresults_by_bid_list(related_bidnos)
        biz_counter += len(related_bidresults)
        biz_data = {}
        
        for bidresult in related_bidresults:
            biz_no = bidresult[4]
            if biz_no not in biz_data:
                # 값이 없으면 초기화
                biz_data[biz_no] = {
                    "rank_sum": 0,
                    "count": 0,
                    "bidDiff_sum": 0,
                    "squared_diff_sum": 0,
                    "bizName": None,
                    "bizOwner": None
                }

            biz_data[biz_no]["rank_sum"] += bidresult[5]
            biz_data[biz_no]["count"] += 1
            biz_data[biz_no]["bidDiff_sum"] += bidresult[8]
            
            if biz_data[biz_no]["bizName"] is None:
                biz_data[biz_no]["bizName"] = bidresult[2]
            if biz_data[biz_no]["bizOwner"] is None:
                biz_data[biz_no]["bizOwner"] = bidresult[3]

        for biz_no in biz_data:
            biz_data[biz_no]["rank_mean"] = biz_data[biz_no]["rank_sum"] / biz_data[biz_no]["count"]
            biz_data[biz_no]["bidDiff_mean"] = biz_data[biz_no]["bidDiff_sum"] / biz_data[biz_no]["count"]

        for bidresult in related_bidresults:
            biz_no = bidresult[4]
            biz_data[biz_no]["squared_diff_sum"] += (bidresult[8] - biz_data[biz_no]["bidDiff_mean"]) ** 2

        for biz_no in biz_data:
            biz_data[biz_no]["bidDiff_variance"] = biz_data[biz_no]["squared_diff_sum"] / biz_data[biz_no]["count"]
        return biz_data
    #endregion
    
    # 검색한 공고의 데이터가 db에 있는지 확인한다
    bid_no = input_value
    bid = data_module.fetch_bid_by_bid_no(bid_no)
    if not bid:
        common.search_status.text = '데이터가 없습니다.'
        return

    # 검색한 공고의 연관 공고(지역과 면허가 겹치는 공고)를 찾는다
    bid_regions = data_module.fetch_bid_regions(bid_no)
    bid_licenses = data_module.fetch_bid_licenses(bid_no)

    bid_filters = set()
    for region in bid_regions:
        for license in bid_licenses:
            bid_filters.add((region[2], license[4]))
    for filter in bid_filters:
        print(filter)
        layout.update_datatable(get_biz_data(filter[0], filter[1]))

    common.search_status.text = f'{bid_counter}개의 공고에서 {biz_counter}개의 투찰 기록을 분석하였습니다'



    
    

        
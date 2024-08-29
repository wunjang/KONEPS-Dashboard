import requests
import logging
import Data.public_data_client.api_key as api_key

logger = logging.getLogger('data')
bids_endpoint = 'http://apis.data.go.kr/1230000/BidPublicInfoService05'
bidresults_endpoint = 'http://apis.data.go.kr/1230000/ScsbidInfoService01'

def _request_api_data(url, params, time_out=60):
    params['ServiceKey'] = api_key.get_api_key()
    req = requests.Request('GET', url, params=params)
    prepared = req.prepare()
    logger.debug(f"Requested URL: {prepared.url}")
    
    try:
        response = requests.get(url, params=params, timeout=time_out)
        response.raise_for_status() # 상태 코드가 200이 아닌 경우 예외를 발생시킴
    except requests.exceptions.Timeout:
        logger.warning("Request timed out.")
        return 'timeout'
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request failed: {e}")
        return None
    
    try:
        item = response.json()
    except ValueError:
        logger.warning("Failed to decode JSON.")
        return None
    
    if not item:
        logger.warning("No data found in the response.")
        return None
    
    logger.debug("Request Succeed.")
    return item

def request_bids_by_region_and_industry(region:str, industry:str, date_begin:str, date_end:str, page_no=1):
    """
    Params:
        region: 지역코드
        industry: 업종코드
        date_begin,date_end: 'yyyyMMddhhmm'형식의 문자열
        page_no: 재귀 호출을 위한 패러미터. 변경 하지 말 것
    returns:
        참조: https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000802#/API%20%EB%AA%A9%EB%A1%9D/getBidPblancListInfoCnstwkPPSSrch02
    """
    url = bids_endpoint + '/getBidPblancListInfoCnstwkPPSSrch02'

    num_of_rows = 100 # api응답 시간을 고려한 매직넘버
    params = {
        "inqryDiv": "1",
        "type": "json",
        "inqryBgnDt": date_begin,
        "inqryEndDt": date_end,
        "pageNo": str(page_no),
        "numOfRows": str(num_of_rows),
        "prtcptLmtRgnCd": region,
        "indstrytyCd": industry,
    }
    response = _request_api_data(url=url, params=params)

    if response is None or 'response' not in response or 'body' not in response['response']:
        logger.error('Invalid or empty response from API')
        return None

    total_count = response['response']['body'].get('totalCount', 0)
    items = response['response']['body'].get('items', [])

    if total_count == 0 or not items:
        logger.info('Items not found from request')
        return None
    
    if page_no == 1:
        logger.info(f"Items count: {total_count}")

    if total_count > num_of_rows * page_no:
        next_page_items = request_bids_by_region_and_industry(region, industry, date_begin, date_end, page_no + 1)
        if next_page_items:
            items.extend(next_page_items)
    return items

def request_bid_by_bid_no(bid_no):
    """
    참조: https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000802#/API%20%EB%AA%A9%EB%A1%9D/getBidPblancListInfoCnstwk02
    """
    url = url = bids_endpoint + '/getBidPblancListInfoCnstwk02'

    num_of_rows = 999
    params = {
        "numOfRows": str(num_of_rows),
        "pageNo": '1',
        "inqryDiv": '2',
        "bidNtceNo": bid_no,
        "type": "json"
    }
    response = _request_api_data(url=url, params=params)

    if response is None or 'response' not in response or 'body' not in response['response']:
        logger.error('Invalid or empty response from API')
        return None
    
    total_count = response['response']['body'].get('totalCount', 0)
    item = response['response']['body'].get('items', [])

    if total_count == 0 or not item:
        logger.warning('Items not found from request')
        return None
    
    return item[0]

def request_bid_detail(bid_no):
    """
    Return: 
    - (a값, 기초가격, 예가범위, 순공사원가)
    """
    url = bids_endpoint + '/getBidPblancListInfoCnstwkBsisAmount02'

    num_of_rows = 999
    params = {
        "numOfRows": str(num_of_rows),
        "pageNo": '1',
        "inqryDiv": '2',
        "bidNtceNo": bid_no,
        "type": "json"
    }
    response = _request_api_data(url=url, params=params)

    if response is None or 'response' not in response or 'body' not in response['response']:
        logger.error('Invalid or empty response from API')
        return None

    total_count = response['response']['body'].get('totalCount', 0)
    items = response['response']['body'].get('items', [])

    if total_count == 0 or not items:
        logger.warning('Items not found from request')
        return None
    
    item = items[0]
    base_price = int(item['bssamt'])
    price_range = abs(int(item['rsrvtnPrceRngBgnRate']))
    d_value = int(item['bssAmtPurcnstcst'] or 0)
    a_value = 0
    if item['bidPrceCalclAYn'] == 'Y':
        a_value += int(item['npnInsrprm']) # 국민연금보험료
        + int(item['mrfnHealthInsrprm']) # 국민건강보험료
        + int(item['rtrfundNon']) # 퇴직공제부금비
        + int(item['odsnLngtrmrcprInsrprm']) # 노인장기요양보험료
        + int(item['sftyMngcst']) # 산업안전보건관리비
        + int(item['sftyChckMngcst']) # 안전관리비
        + int(item['qltyMngcst']) # 품질관리비
    return a_value, base_price, price_range, d_value

def request_region_restriction(bid_no, bid_ord):
    pass

def request_licence_requirements(bid_no, bid_ord):
    pass

def request_bidresults(bid_no:str, page_no=1):
    # TODO. 재입찰 고려
    url = bidresults_endpoint + '/getOpengResultListInfoOpengCompt01'
    num_of_rows = 999
    params = {
        "numOfRows": str(num_of_rows),
        "pageNo": str(page_no),
        "bidNtceNo": bid_no,
        "type": "json"
    }
    response = _request_api_data(url=url, params=params)

    if response is None or 'response' not in response or 'body' not in response['response']:
        logger.error('Invalid or empty response from API')
        return None
    
    total_count = response['response']['body'].get('totalCount', 0)
    items = response['response']['body'].get('items', [])

    if total_count == 0 or not items:
        logger.info('Items not found from request')
        return None
    
    if total_count > num_of_rows * page_no:
        next_page_items = request_bidresults(bid_no, page_no + 1)
        if next_page_items:
            items.extend(next_page_items)
    return items


def request_plan_price(bid_no:str):
    url = bidresults_endpoint + '/getOpengResultListInfoCnstwkPreparPcDetail01'
    params = {
        "numOfRows": '999',
        "pageNo": '1',
        "inqryDiv": '2',
        "bidNtceNo": bid_no,
        "type": "json"
    }
    response = _request_api_data(url=url, params=params)

    if response is None or 'response' not in response or 'body' not in response['response']:
        logger.error('Invalid or empty response from API')
        return None
    
    if response['response']['body']['totalCount'] == 0:
        logger.info(f'Bid:{bid_no} has no plan price. Check if bid has not opened.')
        return 'NO_DATA'
    
    result = response['response']['body']['items'][0]['plnprc']
    if result is None:
        logger.error(f'Invalid plan price value: {result}')
        return None
    return result
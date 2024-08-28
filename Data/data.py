import psycopg2
import datetime
from datetime import datetime, date
import logging
import traceback

logger = logging.getLogger('data')
def _execute_query(query, params=None, fetch_results=True, many=False):
  try:
    conn = psycopg2.connect(
        host="bidinfo-postgre.cj6ccwc4ihjw.ap-southeast-2.rds.amazonaws.com",
        port="5432",
        database="bidinfo",
        user="root"
    )
    with conn.cursor() as cur:
      if many:
        cur.executemany(query, params)
      else:
        cur.execute(query, params)

      if fetch_results:
        # for fetch data
        result = cur.fetchall()
      else:
        # for update data
        conn.commit()
        result = True
    return result
  except Exception as e:
    logger.error(f"An error occurred: {e}")
    logger.error(traceback.format_exc())
    return None
  finally:
    if conn:
      conn.close()

def update_single(query, params=None):
  return _execute_query(query, params, many=False, fetch_results=False)

def update_many(query, params_list=None):
  return _execute_query(query, params_list, many=True, fetch_results=False)

def fetch_single(query, params=None):
  return _execute_query(query, params, many=False, fetch_results=True)
  
def fetch_bidresults_by_bid(bid_no):
  """
  Parameters:
  - bid_no(int): 공고번호
  Returns:
  - (id,공고번호,업체명,대표명,사업자번호,순위,입찰액,투찰율,사정율,예가범위,공고일자,참여업체)
  """
  query = """
    SELECT 
        br.*,
        b.pricerange,
        b.biddate,
        b.biz_count
    FROM 
        bidresults br
    JOIN 
        bids b
    ON 
        br.bidno = b.bidno
    WHERE 
        br.bidno = %s;
    """
  params = (bid_no,)
  result = fetch_single(query, params)
  names = ['id','bid_no','biz_name','biz_owner','biz_no','rank','bid_price','bid_ratio','bid_diff','price_range','bid_date','biz_count']
  return result

def fetch_bid_by_bid_no(bid_no):
  """
  Parameters:
  - bid_no(int): 공고번호
  Returns:
  - (공고번호,순공사원가사용여부,입찰하한가,기초가격,A값,자격요건,공고차수,취소여부,예가범위,순공사원가액수,공고일자,참여업체)
  """
  query = "SELECT * FROM bids WHERE bidno = %s"
  params = (bid_no,)
  result = fetch_single(query, params)
  names = ["bid_no", "is_using_d_value", "bid_min", "base_price", "a_value", "industry", "bid_ord", "is_canceled", "price_range", "d_value", "bid_date", "biz_count"]
  return tuple_to_dict(names, result[0])

def fetch_bid_no_list(bid_no_min, bid_no_max):
  """
  중복 체크를 위해 bid_no 값만 반환
  """
  query = """
  SELECT b.bidno FROM bids b WHERE b.bidno >= %s AND b.bidno <= %s
  """
  params = (bid_no_min, bid_no_max)
  result = fetch_single(query, params)
  return result

def fetch_bids_without_results():
  """
  개찰 결과가 업데이트 되지 않은 공고들만 체크
  """
  query = """
  SELECT b.bidno FROM bids b WHERE (b.biz_count = 0 OR b.biz_count IS NULL) AND b.iscanceled = False
  """
  params = ()
  result = fetch_single(query, params)
  return result

def fetch_bidresults_by_biz(biz_no):
  """
  Parameters:
  - biz_no(int): 사업자번호
  - date_begin(datetime): 필터링할 날짜 구간의 시작일
  - date_end(datetime): 필터링할 날짜 구간의 종료일
  Returns:
  - (id,공고번호,업체명,대표명,사업자번호,순위,입찰액,투찰율,사정율,예가범위,공고일자,참여업체)
  """
  query = """
  SELECT 
      br.*,
      b.pricerange,
      b.biddate,
      b.biz_count
  FROM 
      bidresults br
  JOIN 
      bids b
  ON 
      br.bidno = b.bidno
  WHERE 
      br.bizno = %s
  """
  params = (biz_no,)
  result = fetch_single(query, params)
  return result

def filter_bidresults(data_list, date_begin=None, date_end=None, price_range=None, biz_count_min=None, biz_count_max=None):
  if not data_list:
    return data_list
  
  if date_begin and date_end:
    try:
      date_begin = datetime.strptime(date_begin, '%Y-%m-%d').date()
      date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
    except ValueError as e:
      #TODO. 여기서 ValueError가 나기는 아주 쉬울 것 같다... popup을 띄운다거나 해서 유저에게 알려야 함
      date_begin = None
      date_end = None
  
  def apply_filters(data):
    return (
            (not isinstance(date_begin, date) or data[10] >= date_begin) and
            (not isinstance(date_end, date) or data[10] <= date_end) and
            (not isinstance(price_range, int) or data[9] == price_range) and
            (not isinstance(biz_count_min, int) or data[11] >= biz_count_min) and
            (not isinstance(biz_count_max, int) or data[11] <= biz_count_max)
        )
  
  filtered_list = [data for data in data_list if apply_filters(data)]
  return filtered_list

def tuple_to_dict(names, tuple):
  return {name: value for name, value in zip(names, tuple)}
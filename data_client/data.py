import psycopg2
from psycopg2 import sql
import datetime
from datetime import datetime, date
import logging
import traceback

logger = logging.getLogger('data_client')
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
  
def fetch_bidresults_by_bid_no(bid_no):
  """
  Parameters:
    bid_no(int): 공고번호
  Returns:
    (id,공고번호,업체명,대표명,사업자번호,순위,입찰액,투찰율,사정율,예가범위,공고일자,참여업체)
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
  Params:
    bid_no(int): 공고번호
  Returns:
    (공고번호,순공사원가사용여부,입찰하한가,기초가격,A값,자격요건,공고차수,취소여부,예가범위,순공사원가액수,공고일자,참여업체)
  """
  query = "SELECT * FROM bids WHERE bidno = %s"
  params = (bid_no,)
  result = fetch_single(query, params)
  if not result:
    return ()
  names = ["bid_no", "is_using_d_value", "bid_min", "base_price", "a_value", "industry", "bid_ord", "is_canceled", "price_range", "d_value", "bid_date", "biz_count"]
  return tuple_to_dict(names, result[0])

def fetch_bids_by_region_and_license(region, license):
  """
  Params:
    region(str): 지역코드
    industry(str): 업종코드
  Returns:
    (공고번호,순공사원가사용여부,입찰하한가,기초가격,A값,자격요건,공고차수,취소여부,예가범위,순공사원가액수,공고일자,참여업체)
  """
  query = """
  SELECT b.*
  FROM bids b
  JOIN bidregions br ON b.bidno = br.bidno
  JOIN bidlicense bl ON b.bidno = bl.bidno
  WHERE br.region = %s AND bl.license_code = %s;
  """
  params = (region, license)
  results = fetch_single(query, params)
  if not results:
    return ()
  return results

def fetch_bid_regions(bid_no):
  """
  Returns:
    (id,공고번호,지역)
  """
  query = "SELECT * FROM bidregions WHERE bidno = %s"
  params = (bid_no,)
  results = fetch_single(query, params)
  if not results:
    return ()
  return results

def fetch_bid_licenses(bid_no):
  """
  Returns:
    (id,공고번호,업종코드,그룹)
  """
  query = "SELECT * FROM bidlicense WHERE bidno = %s"
  params = (bid_no,)
  results = fetch_single(query, params)
  if not results:
    return ()
  return results

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

def fetch_bids_without_results(date_begin, date_end):
  """
  개찰 결과가 업데이트 되지 않은 공고들만 체크
  """
  query = """
  SELECT b.bidno FROM bids b WHERE (b.biz_count = 0 OR b.biz_count IS NULL) AND b.iscanceled = False AND b.biddate >= %s AND b.biddate <= %s
  """
  params = (date_begin, date_end)
  result = fetch_single(query, params)
  return result

def fetch_bidresults_by_biz(biz_no):
  """
  Params:
    biz_no(int): 사업자번호
  Returns:
    (id,공고번호,업체명,대표명,사업자번호,순위,입찰액,투찰율,사정율,예가범위,공고일자,참여업체)
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

def fetch_bidresults_by_bid_list(bid_no_list):
  """
  Returns:
    (0.id,1.공고번호,2.업체명,3.대표명,4.사업자번호,5.순위,6.입찰액,7.투찰율,8.사정율,9.예가범위,10.공고일자,11.참여업체)
  """
  query = "SELECT * FROM bidresults WHERE bidno = ANY(%s::text[])"
  return fetch_single(query, (bid_no_list,))

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
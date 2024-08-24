import psycopg2
import datetime
import logging
import traceback

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
    logging.error(f"An error occurred: {e}")
    logging.error(traceback.format_exc())
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
  
  def apply_filters(data):
    return (
            (not isinstance(date_begin, datetime.date) or data[10] >= date_begin) and
            (not isinstance(date_end, datetime.date) or data[10] <= date_end) and
            (not isinstance(price_range, int) or data[9] == price_range) and
            (not isinstance(biz_count_min, int) or data[11] >= biz_count_min) and
            (not isinstance(biz_count_max, int) or data[11] <= biz_count_max)
        )
  
  filtered_list = [data for data in data_list if apply_filters(data)]
  return filtered_list

def tuple_to_dict(names, tuple):
  return {name: value for name, value in zip(names, tuple)}
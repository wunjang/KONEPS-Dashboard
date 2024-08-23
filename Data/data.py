import psycopg2
import datetime

def execute_query(query, params=None):
  try:
    conn = psycopg2.connect(
        host="bidinfo-postgre.cj6ccwc4ihjw.ap-southeast-2.rds.amazonaws.com",
        port="5432",
        database="bidinfo",
        user="root"
    )
    with conn.cursor() as cur:
      cur.execute(query, params)
      result = cur.fetchall()
    return  result
  except Exception as e:
    print(f"An error occurred: {e}")
    return None
  finally:
    if conn:
      conn.close()
  
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
  result = execute_query(query, params)
  return result

def fetch_bids_by_bid(bid_no):
  """
  Parameters:
  - bid_no(int): 공고번호
  Returns:
  - (공고번호,순공사원가사용여부,입찰하한가,기초가격,A값,자격요건,공고차수,취소여부,예가범위,순공사원가액수,공고일자)
  """
  query = "SELECT * FROM bids WHERE bidno = %s"
  params = (bid_no,)
  result = execute_query(query, params)
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
  result = execute_query(query, params)
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
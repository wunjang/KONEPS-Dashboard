import psycopg2
from datetime import datetime

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
  - (id,공고번호,업체명,대표명,사업자번호,등수,입찰액,투찰율,사정율,예가범위,공고일자)
  """
  query = """
    SELECT 
        br.*,
        b.pricerange,
        b.biddate
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

def fetch_bidresults_by_biz(biz_no, date_begin: datetime=None, date_end: datetime=None):
  """
  Parameters:
  - biz_no(int): 사업자번호
  Returns:
  - (id,공고번호,업체명,대표명,사업자번호,등수,입찰액,투찰율,사정율,예가범위,공고일자)
  """
  if isinstance(date_begin, datetime) and isinstance(date_end, datetime):
    query = """
    SELECT 
        br.*,
        b.pricerange,
        b.biddate
    FROM 
        bidresults br
    JOIN 
        bids b
    ON 
        br.bidno = b.bidno
    WHERE 
        br.bizno = %s AND
        br.biddate >= %s AND
        br.biddate <= %s;
    """
    date_begin_str = date_begin.strftime('%Y-%m-%d %H:%M:%S')
    date_end_str = date_end.strftime('%Y-%m-%d %H:%M:%S')
    params = (biz_no, date_begin_str, date_end_str)
  else:
    query = """
      SELECT 
          br.*,
          b.pricerange,
          b.biddate
      FROM 
          bidresults br
      JOIN 
          bids b
      ON 
          br.bidno = b.bidno
      WHERE 
          br.bizno = %s;
      """
    params = (biz_no,)
  result = execute_query(query, params)
  return result
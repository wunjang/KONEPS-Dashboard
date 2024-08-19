import psycopg2

def GetConnection():
  try:
    conn = psycopg2.connect(
        host="bidinfo-postgre.cj6ccwc4ihjw.ap-southeast-2.rds.amazonaws.com",
        port="5432",
        database="bidinfo",
        user="root"
    )
    print("Database connection established")
    return  conn
  except Exception as e:
    print(f"An error occurred: {e}")
    return 0
  
def GetBidResultsByBidNo(bidNo, isPrint=False):
  """
  Parameters:
  - bidNo(int): 공고번호
  Returns:
  - (id,공고번호,업체명,대표명,사업자번호,등수,입찰액,투찰율,사정율,예가범위,공고일자)
  """
  conn = GetConnection()
  if conn == 0:
    return
  cur = conn.cursor()

  query = f"""
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
        br.bidno = '{bidNo}';
    """
  cur.execute(query)
  result = cur.fetchall()
 
  cur.close()
  conn.close()
  if isPrint:
    print(result)
  return result

def GetBidsByBidNo(bidNo, isPrint=False):
  """
  Parameters:
  - bidNo(int): 공고번호
  Returns:
  - (공고번호,순공사원가사용여부,입찰하한가,기초가격,A값,자격요건,공고차수,취소여부,예가범위,순공사원가액수,공고일자)
  """
  conn = GetConnection()
  if conn == 0:
    return
  cur = conn.cursor()

  query = f"SELECT * FROM bids WHERE bidno = '{bidNo}'"
  cur.execute(query)
  result = cur.fetchall()
 
  cur.close()
  conn.close()
  if isPrint:
    print(result)
  return result

def GetBidResultsByBizNo(bizNo, isPrint=False):
  """
  Parameters:
  - bizNo(int): 사업자번호
  Returns:
  - (id,공고번호,업체명,대표명,사업자번호,등수,입찰액,투찰율,사정율,예가범위,공고일자)
  """
  conn = GetConnection()
  if conn == 0:
    return
  cur = conn.cursor()
  query = f"""
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
        br.bizno = '{bizNo}';
    """
  cur.execute(query)
  result = cur.fetchall()
  
  cur.close()
  conn.close()
  if isPrint:
    print(result)
  return result
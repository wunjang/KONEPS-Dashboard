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
  
def GetBidResultsByBidNo(bidNo):
  """
  Parameters:
  - bidNo(int): 공고번호
  Returns:
  - (id,공고번호,업체명,대표명,사업자번호,등수,입찰액,투찰율,사정율)
  """
  conn = GetConnection()
  if conn == 0:
    return
  cur = conn.cursor()

  query = f"SELECT * FROM bidresults WHERE bidno = '{bidNo}'"
  cur.execute(query)
  result = cur.fetchall()
 
  cur.close()
  conn.close()
  return result

def GetBizResultsByBizNo(bizNo):
  """
  Parameters:
  - bizNo(int): 사업자번호
  Returns:
  - (id,공고번호,업체명,대표명,사업자번호,등수,입찰액,투찰율,사정율)
  """
  conn = GetConnection()
  if conn == 0:
    return
  cur = conn.cursor()

  query = f"SELECT * FROM bidresults WHERE bizno = '{bizNo}'"
  cur.execute(query)
  result = cur.fetchall()
  
  cur.close()
  conn.close()
  return result
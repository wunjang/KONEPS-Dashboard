import Data.data as data_module
import Data.data_update as update_module
from datetime import date, timedelta
import logging

def check_finished_bid():
    """
    개찰이 완료되었으나 결과가 업데이트 되지 않은 입찰을 확인하고 업데이트한다
    """

def daily_update():
    """
    매일 자동으로 실행되는 코드
    """
    today = date.today()
    logging.info(f"Daily update for {today}")
    yesterday = today - timedelta(days=1)
    today_str = today.strftime('%Y%m%d') + "0000"
    yesterday_str = yesterday.strftime('%Y%m%d') + "0000"
    update_module.update_bids('44', '4993', today_str, yesterday_str)
    check_finished_bid()

def do_update():
    update_module.update_bids('44','4993','202402010000','202403010000')
    update_module.update_bids('44','4993','202403010000','202404010000')
    update_module.update_bids('44','4993','202404010000','202405010000')
    update_module.update_bids('44','4993','202405010000','202406010000')
    update_module.update_bids('44','4993','202406010000','202407010000')
    update_module.update_bids('44','4993','202407010000','202408010000')
    logging.info("Comeplete: do_update()")

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
do_update()
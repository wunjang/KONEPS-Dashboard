import Data.data as data_module
import Data.data_update as update_module
from datetime import date, timedelta, datetime
import logging
import sys
import argparse

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

def parse_log_level(log_level_str):
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    if log_level_str in log_levels:
        return log_levels[log_level_str]
    
    elif log_level_str.isdecimal() and 0 < int(log_level_str) < 50:
        return int(log_level_str)
    
    return logging.WARNING # Default

def logging_config(log_level:int, print_console:bool):
    logger = logging.getLogger("data")
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler("DBupdater.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if print_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def check_valid_date(date_str:str)->bool:
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(description="Example script with named arguments.")
    parser.add_argument('--log_level', type=str, help='log level', default='WARNING')
    parser.add_argument('--print', type=bool, help='print logs on console', default='False')
    #TODO. 특정 공고 업데이트 기능
    #parser.add_argument('--bid_no', type=str, help='find and update bid of bid_no')
    parser.add_argument('--bid_date', type=str, help='find and update bids of a single day, format: yyyyMMdd')
    args = parser.parse_args()

    # logging config
    log_level = parse_log_level(args.log_level)
    logger = logging_config(log_level, args.print)

    if args.bid_date and check_valid_date(args.bid_date):
        update_module.update_bids('44', '4993', args.bid_date + '0000', args.bid_date + '2359')

if __name__ == "__main__":
    main()
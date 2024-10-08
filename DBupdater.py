import data_client.data_update as update_module
import data_client.data as data_module
from datetime import date, timedelta, datetime
import logging
import argparse
import log.utils
from concurrent.futures import ThreadPoolExecutor

def daily_update(reprocess):
    """
    매일 자동으로 실행되는 코드
    어제 올라온 공고를 업데이트 한다
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    year_ago = today - timedelta(days=365)
    today_str = today.strftime('%Y%m%d') + "0000"
    yesterday_str = yesterday.strftime('%Y%m%d') + "0000"
    update_module.update_bids('44', '4993', date_end=today_str, date_begin=yesterday_str, reprocess=reprocess)
    update_module.update_finished_bid(reprocess, date_begin=year_ago, date_end=today)

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

def check_valid_date(date_str:str)->bool:
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(description="Example script with named arguments.")
    parser.add_argument('--log_level', type=str, help='log level', default='WARNING')
    parser.add_argument('--bid_no', type=str, help='find and update bid of bid_no')
    parser.add_argument('--bid_date', type=str, help='find and update bids of a single day, format: yyyyMMdd')
    parser.add_argument('--print', action='store_true', help='print logs on console')
    parser.add_argument('--reprocess', action='store_true', help='process data already exist in database')
    
    # sub command
    subparser = parser.add_subparsers(dest="command")
    subparser.add_parser("daily_update", help="Excute daily update")

    args = parser.parse_args()

    # logging config
    log_level = parse_log_level(args.log_level)
    logger = log.utils.add_logger(name='data_client', log_level=log_level)

    if args.bid_no:
        update_module.update_bid(str(args.bid_no), args.reprocess)

    if args.bid_date and check_valid_date(args.bid_date):
        update_module.update_bids('44', '4993', args.bid_date + '0000', args.bid_date + '2359', args.reprocess)

    if args.command == "daily_update":
        logger.info(f"=====Daily update for {date.today()} begin=====")
        daily_update(args.reprocess)
        logger.info("=====Daily update end=====")


if __name__ == "__main__":
    main()
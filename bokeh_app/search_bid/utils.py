from datetime import datetime, date
import pandas as pd

def reflect_url(params):
    pass

def filter_data(data, date_begin=None, date_end=None, price_range=None, biz_count_min=None, biz_count_max=None):
    df = pd.DataFrame(data)
    if date_begin and date_end:
        try:
            date_begin = datetime.strptime(date_begin, '%Y-%m-%d').date()
            date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        except ValueError as e:
            date_begin = None
            date_end = None
    if isinstance(price_range, str) and price_range.isdigit():
        price_range = int(price_range)

    if isinstance(date_begin, date):
        df = df[df['bidDate'] >= date_begin]
    if isinstance(date_end, date):
        df = df[df['bidDate'] <= date_end]
    if isinstance(price_range, int):
        df = df[df['priceRange'] == price_range]
    if isinstance(biz_count_min, int):
        df = df[df['biz_count'] >= biz_count_min]
    if isinstance(biz_count_max, int):
        df = df[df['biz_count'] <= biz_count_max]
    return df
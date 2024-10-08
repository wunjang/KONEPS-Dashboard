import data_client.data as data_module
import data_client.public_data_client.data_request as request_module
import logging
import traceback

logger = logging.getLogger('data_client')
def update_bids(region:str, industry:str, date_begin:str, date_end:str, reprocess:bool):
    """
    Params:
        region: 지역코드
        industry: 업종코드
        date_begin,date_end: 검색할 공고일자 구간. 'yyyyMMddhhmm'형식
    """
    params_list = []
    bids = request_module.request_bids_by_region_and_industry(region, industry, date_begin, date_end)
    if not bids:
        return

    if reprocess is False:
        check_list = data_module.fetch_bid_no_list(bids[0]['bidNtceNo'], bids[len(bids)-1]['bidNtceNo'])
        bids = [bid for bid in bids if bid['bidNtceNo'] not in check_list]

    for index, bid in enumerate(bids):
        try:
            bid_no = bid['bidNtceNo']
            bid_ord = bid['bidNtceOrd']
            logger.info(f"Processing bid: {bid_no}-{bid_ord}... Progress: {index+1}/{len(bids)}({((index+1)/len(bids))*100:.2f}%)")
            is_canceled = bid['ntceKindNm'] == '취소'
            if not bid_no.isdigit():
                # 국방부공고 - 별도 작업으로 분리
                logger.info(f"bidNo: {bid_no}-{bid_ord} is unusual bid notice and will not be updated in the database.")
                continue
            elif is_canceled:
                continue
            
            bid_detail = request_module.request_bid_detail(bid_no)
            if not bid_detail:
                logger.warning(f"Failed to find bid detail for bid: {bid_no}")
                continue
            a_value, base_price, price_range, d_value = bid_detail

            plan_price = request_module.request_plan_price(bid_no)
            if plan_price == 'NO_DATA':
                plan_price = None
            elif not plan_price:
                logger.warning(f"Failed to find plan price for bid: {bid_no}")
                continue
            else:
                plan_price = int(float(plan_price))

            params_list.append({
                "bidNo": bid_no,
                "isUsingD": d_value != 0,
                "bidMin": bid['sucsfbidLwltRate'] or 0,
                "basePrice": base_price,
                "AVal": a_value,
                "industry": "-", #별개 테이블로 분리 예정
                "bidOrd": bid_ord,
                "planprice": plan_price,
                "iscanceled": is_canceled,
                "priceRange": price_range,
                "DVal": d_value,
                "bidDate": bid['bidNtceDt']
            })
        except Exception as e:
            logger.error(f"Update failed by exception: {e}, while processing data: {bid}")
            logger.error(traceback.format_exc())
            continue
    logger.debug(f"{len(params_list)} bid data ready for update.")

    query = """
        INSERT INTO Bids (bidNo, isUsingD, bidMin, basePrice, AVal, industry, bidOrd, planprice, iscanceled, priceRange, DVal, bidDate) 
        VALUES (%(bidNo)s, %(isUsingD)s, %(bidMin)s, %(basePrice)s, %(AVal)s, %(industry)s, %(bidOrd)s, %(planprice)s, %(iscanceled)s, %(priceRange)s, %(DVal)s, TO_TIMESTAMP(%(bidDate)s, 'YYYY-MM-DD HH24:MI:SS'))
        ON CONFLICT (bidNo)
        DO UPDATE SET
            isUsingD = EXCLUDED.isUsingD,
            bidMin = EXCLUDED.bidMin,
            basePrice = EXCLUDED.basePrice,
            AVal = EXCLUDED.AVal,
            industry = EXCLUDED.industry,
            bidOrd = EXCLUDED.bidOrd,
            planprice = EXCLUDED.planprice,
            iscanceled = EXCLUDED.iscanceled,
            priceRange = EXCLUDED.priceRange,
            DVal = EXCLUDED.DVal,
            bidDate = EXCLUDED.bidDate
        WHERE Bids.bidOrd < EXCLUDED.bidOrd
        """
    result = data_module.update_many(query, params_list)
    if result:
        logger.info(f"Complete: update_bids().")
        for index, bid in enumerate(params_list):
            logger.info(f"Processing additional data of bid: {bid['bidNo']}-{bid['bidOrd']}... Progress: {index+1}/{len(params_list)}({((index+1)/len(params_list))*100:.2f}%)")
            update_bidresults(bid['bidNo'], reprocess)
            update_bid_license(bid['bidNo'], bid['bidOrd'])
            update_bid_region(bid['bidNo'], bid['bidOrd'])

def update_bid(bid_no, reprocess:bool):
    """
    Todo:
        update_bids()랑 코드가 많이 겹치는데 좀 줄여보자
    """
    bid = request_module.request_bid_by_bid_no(bid_no)
    if not bid:
        return
    try:
        bid_no = bid['bidNtceNo']
        bid_ord = bid['bidNtceOrd']
        logger.info(f"Processing single bid: {bid_no}-{bid_ord}...")
        is_canceled = bid['ntceKindNm'] == '취소'
        if not bid_no.isdigit():
            # 국방부공고 - 별도 작업으로 분리
            logger.info(f"bidNo: {bid_no}-{bid_ord} is unusual bid notice and will not be updated in the database.")
            return
        elif is_canceled:
            return
        
        bid_detail = request_module.request_bid_detail(bid_no)
        if not bid_detail:
            logger.warning(f"Failed to find bid detail for bid: {bid_no}")
            return
        a_value, base_price, price_range, d_value = bid_detail

        plan_price = request_module.request_plan_price(bid_no)
        if plan_price == 'NO_DATA':
            plan_price = None
        elif not plan_price:
            logger.warning(f"Failed to find plan price for bid: {bid_no}")
            return
        else:
            plan_price = int(float(plan_price))

        params = {
            "bidNo": bid_no,
            "isUsingD": d_value != 0,
            "bidMin": bid['sucsfbidLwltRate'] or 0,
            "basePrice": base_price,
            "AVal": a_value,
            "industry": "-", #별개 테이블로 분리 예정
            "bidOrd": bid_ord,
            "planprice": plan_price,
            "iscanceled": is_canceled,
            "priceRange": price_range,
            "DVal": d_value,
            "bidDate": bid['bidNtceDt']
        }
    except Exception as e:
        logger.error(f"Update failed by exception: {e}, while processing data: {bid}")
        logger.error(traceback.format_exc())
        return
    
    query = """
        INSERT INTO Bids (bidNo, isUsingD, bidMin, basePrice, AVal, industry, bidOrd, planprice, iscanceled, priceRange, DVal, bidDate) 
        VALUES (%(bidNo)s, %(isUsingD)s, %(bidMin)s, %(basePrice)s, %(AVal)s, %(industry)s, %(bidOrd)s, %(planprice)s, %(iscanceled)s, %(priceRange)s, %(DVal)s, TO_TIMESTAMP(%(bidDate)s, 'YYYY-MM-DD HH24:MI:SS'))
        ON CONFLICT (bidNo)
        DO UPDATE SET
            isUsingD = EXCLUDED.isUsingD,
            bidMin = EXCLUDED.bidMin,
            basePrice = EXCLUDED.basePrice,
            AVal = EXCLUDED.AVal,
            industry = EXCLUDED.industry,
            bidOrd = EXCLUDED.bidOrd,
            planprice = EXCLUDED.planprice,
            iscanceled = EXCLUDED.iscanceled,
            priceRange = EXCLUDED.priceRange,
            DVal = EXCLUDED.DVal,
            bidDate = EXCLUDED.bidDate
        WHERE Bids.bidOrd < EXCLUDED.bidOrd
        """
    result = data_module.update_single(query, params)
    if result:
        logger.info(f"Complete: update_bid().")
        update_bidresults(bid_no, reprocess)
        update_bid_license(bid_no, bid_ord)
        update_bid_region(bid_no, bid_ord)
            

def update_bidresults(bid_no, reprocess:bool):
    params_list = []
    bidresults = request_module.request_bidresults(bid_no)
    if not bidresults:
        return
    
    # bidrank 음수 순위 책정
    bidresults = sorted(bidresults, key=lambda x: x['bidprcAmt'], reverse=True)
    negetive_rank = -1
    for bidresult in bidresults:
        if not bidresult['opengRank']:
            bidresult['opengRank'] = negetive_rank
            negetive_rank -= 1
    
    bid = data_module.fetch_bid_by_bid_no(bid_no)
    for index, bidresult in enumerate(bidresults):
        logger.debug(f"Processing bidresults of bid: {bid_no}... Progress: {index+1}/{len(bidresults)}({((index+1)/len(bidresults))*100:.2f}%)")
        try:
            bid_price = int(bidresult['bidprcAmt'] or 0)
            a_value = int(bid["a_value"])
            bid_min = float(bid["bid_min"])
            base_price = int(bid["base_price"])
            params_list.append({
                "bidno": bid_no,
                "bizname": bidresult['prcbdrNm'],
                "bizowner": bidresult['prcbdrCeoNm'],
                "bizno": bidresult['prcbdrBizno'],
                "bidrank": bidresult['opengRank'] or -1,
                "bidprice": bid_price,
                "bidratio": bidresult['bidprcrt'] or 0,
                "biddiff": ((bid_price - a_value) / (bid_min / 100) + a_value) / base_price
            })
        except Exception as e:
            logger.error(f"Update failed by exception: {e}, while processing data: {bidresult}")
            logger.error(traceback.format_exc())
            continue
    logger.debug(f"{len(params_list)} bidresult data ready for update.")

    query = """
        INSERT INTO bidresults (bidno, bizname, bizowner, bizno, bidrank, bidprice, bidratio, biddiff) 
        VALUES (%(bidno)s, %(bizname)s, %(bizowner)s, %(bizno)s, %(bidrank)s, %(bidprice)s, %(bidratio)s, %(biddiff)s)
        ON CONFLICT (bidNo, bizNo) DO NOTHING;
    """
    result = data_module.update_many(query, params_list)
    if result:
        logger.debug(f"Complete: update_bidresults().")
        update_bid_biz_count(bid_no, len(bidresults))
    
def update_bid_biz_count(bid_no, biz_count):
    query = """
        UPDATE bids
        SET biz_count = %(biz_count)s
        WHERE bids.bidno = %(bidno)s
        """
    params = {
        "bidno": bid_no,
        "biz_count": biz_count
    }
    result = data_module.update_single(query, params)
    if result:
        logger.debug(f"Complete: update_bid_biz_count().")

def update_finished_bid(reprocess:bool, date_begin, date_end):
    """
    개찰이 완료되었으나 결과가 업데이트 되지 않은 입찰을 확인하고 업데이트한다
    """
    bids = data_module.fetch_bids_without_results(date_begin, date_end)
    if not bids:
        return
    for index, bid in enumerate(bids):
        logger.info(f"Processing finished bid: {bid[0]}... Progress: {index+1}/{len(bids)}({((index+1)/len(bids))*100:.2f}%)")
        update_bidresults(bid[0], reprocess)

def update_bid_region(bid_no, bid_ord):
    regions = request_module.request_region_restriction(bid_no, bid_ord)
    if not regions:
        return
    params_list = []
    for index, region in enumerate(regions):
        logger.debug(f"Processing region restrictions of bid: {bid_no}... Progress: {index+1}/{len(regions)}({((index+1)/len(regions))*100:.2f}%)")
        try:
            params_list.append({
                "bidno": bid_no,
                "region": region
            })
        except Exception as e:
            logger.error(f"Update failed by exception: {e}, while processing data: {region}")
            logger.error(traceback.format_exc())
            continue
    query = """
        INSERT INTO bidregions (bidno, region)
        VALUES (%(bidno)s, %(region)s)
        ON CONFLICT (bidno, region) 
        DO UPDATE SET region = EXCLUDED.region;
        """
    result = data_module.update_many(query, params_list)
    if result:
        logger.debug(f"Complete: update_bid_region().")

def update_bid_license(bid_no, bid_ord):
    licenses = request_module.request_license_restrictions(bid_no, bid_ord)
    if not licenses:
        return
    params_list = []
    for index, license in enumerate(licenses):
        logger.debug(f"Processing license restrictions of bid: {bid_no}... Progress: {index+1}/{len(licenses)}({((index+1)/len(licenses))*100:.2f}%)")
        try:
            params_list.append({
                "bidno": bid_no,
                "group_no": license[0],
                "license": license[1],
                "license_code": license[1][-4:]
            })
        except Exception as e:
            logger.error(f"Update failed by exception: {e}, while processing data: {license}")
            logger.error(traceback.format_exc())
            continue
    query = """
        INSERT INTO bidlicense (bidno, group_no, license, license_code)
        VALUES (%(bidno)s, %(group_no)s, %(license)s, %(license_code)s)
        ON CONFLICT (bidno, license, group_no) 
        DO UPDATE SET 
            group_no = EXCLUDED.group_no,
            license = EXCLUDED.license,
            license_code = EXCLUDED.license_code;
        """
    result = data_module.update_many(query, params_list)
    if result:
        logger.debug(f"Complete: update_bid_license().")
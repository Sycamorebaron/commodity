import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from multiprocessing.pool import  Pool

from factor.test.cal_factor_realize.rtn_moment import rtn_moment_cal
from factor.test.cal_factor_realize.money_flow import money_flow_cal
from factor.test.cal_factor_realize.vol_amt_split import vol_amt_split_cal
from factor.test.cal_factor_realize.vol_price import vol_price_cal

if __name__ == '__main__':

    pool = Pool(processes=4)

    pool.apply_async(rtn_moment_cal,)
    pool.apply_async(money_flow_cal,)
    pool.apply_async(vol_amt_split_cal,)
    pool.apply_async(vol_price_cal,)

    pool.close()
    pool.join()


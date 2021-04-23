import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from multiprocessing.pool import  Pool

from factor.test.cal_factor_realize.updown_factor import updown_factor_cal
from factor.test.cal_factor_realize.big_factor import big_factor_cal
from factor.test.cal_factor_realize.liquidity import liquidity_cal
from factor.test.cal_factor_realize.singular_vol import singular_vol_cal

if __name__ == '__main__':

    pool = Pool(processes=4)

    pool.apply_async(updown_factor_cal,)
    pool.apply_async(big_factor_cal,)
    pool.apply_async(liquidity_cal,)
    pool.apply_async(singular_vol_cal,)


    pool.close()
    pool.join()

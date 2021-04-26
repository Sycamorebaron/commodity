import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from multiprocessing.pool import  Pool

from factor.test.cal_factor_realize.basis import basis_cal
from factor.test.cal_factor_realize.big_factor import big_factor_cal
from factor.test.cal_factor_realize.liquidity import liquidity_cal
from factor.test.cal_factor_realize.momentum import momentum_cal

from factor.test.cal_factor_realize.money_flow import money_flow_cal
from factor.test.cal_factor_realize.others_factor import others_factor_cal
from factor.test.cal_factor_realize.pca_factor import pca_factor_cal
from factor.test.cal_factor_realize.rtn_factor import rtn_factor_cal

from factor.test.cal_factor_realize.rtn_moment import rtn_moment_cal
from factor.test.cal_factor_realize.singular_vol import singular_vol_cal
from factor.test.cal_factor_realize.updown_factor import updown_factor_cal
from factor.test.cal_factor_realize.vol_amt_split import vol_amt_split_cal

from factor.test.cal_factor_realize.vol_price import vol_price_cal


if __name__ == '__main__':

    pool = Pool(processes=4)

    pool.apply_async(updown_factor_cal, ('2011-01-04', '2021-02-28'))
    pool.apply_async(vol_amt_split_cal, ('2011-01-04', '2021-02-28'))
    pool.apply_async(vol_price_cal, ('2013-01-04', '2021-02-28'))


    pool.close()
    pool.join()

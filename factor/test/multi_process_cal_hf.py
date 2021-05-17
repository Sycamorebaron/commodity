import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from multiprocessing.pool import  Pool

# =========30T
from factor.test.cal_factor_realize_hf.hf_big_factor import hf_big_factor
from factor.test.cal_factor_realize_hf.hf_liquidity import hf_liquidity_pirce
from factor.test.cal_factor_realize_hf.hf_pca import hf_pca_price
from factor.test.cal_factor_realize_hf.hf_rtn_moment import hf_rtn_moment

from factor.test.cal_factor_realize_hf.hf_singular import hf_singular
from factor.test.cal_factor_realize_hf.hf_up_down import hf_up_down
from factor.test.cal_factor_realize_hf.hf_vol_price import hf_vol_pirce


if __name__ == '__main__':

    pool = Pool(processes=4)

    pool.apply_async(hf_pca_price, ('2011-01-01', '2021-02-28'))
    # pool.apply_async(hf_up_down, ('2011-01-01', '2021-02-28'))
    pool.apply_async(hf_vol_pirce, ('2011-01-01', '2021-02-28'))
    # pool.apply_async(hf_rtn_moment, ('2011-01-01', '2021-02-28'))

    pool.close()
    pool.join()

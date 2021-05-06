import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from multiprocessing.pool import  Pool

# =========30T
from factor.test.cal_factor_realize_hf.hf_rtn import hf_rtn


if __name__ == '__main__':

    pool = Pool(processes=4)

    pool.apply_async(hf_rtn, ('2011-01-01', '2013-12-31'))
    pool.apply_async(hf_rtn, ('2014-01-01', '2016-12-31'))
    pool.apply_async(hf_rtn, ('2017-01-01', '2019-12-31'))
    pool.apply_async(hf_rtn, ('2020-01-01', '2021-02-28'))

    pool.close()
    pool.join()

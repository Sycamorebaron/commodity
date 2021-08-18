import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
import gplearn

from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_rtn import hf_rtn_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_rtn_moment import hf_rtn_moment_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_max_min_rtn import hf_max_min_rtn_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_basis_factor import hf_basis_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_big_factor import hf_big_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_leverage_effect_factor import hf_leverage_effect_factor

from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_liquidity import hf_liquidity_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_pca_factor import hf_pca_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_pvcorr_factor import hf_PVCorr_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_simple_price_volume_factor import hf_simple_price_volume_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_singular_factor import hf_singular_factor

from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_updown_factor import hf_updown_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_vol_price import hf_vol_price_factor
from factor.cal_daily_factor_1D.cal_factor_realize.hfd1t_volume_ratio_factor import hf_volume_ratio_factor

# hf_rtn_factor('2011-01-01', '2021-02-28')
# hf_rtn_moment_factor('2011-01-01', '2021-02-28')
# hf_max_min_rtn_factor('2011-01-01', '2021-02-28')
# hf_basis_factor('2011-01-01', '2021-02-28')
# hf_big_factor('2011-01-01', '2021-02-28')
# hf_leverage_effect_factor('2011-01-01', '2021-02-28')
# hf_liquidity_factor('2011-01-01', '2021-02-28')
# hf_pca_factor('2011-01-01', '2021-02-28')

hf_PVCorr_factor('2011-01-01', '2021-02-28')
hf_simple_price_volume_factor('2011-01-01', '2021-02-28')
hf_singular_factor('2011-01-01', '2021-02-28')
hf_updown_factor('2011-01-01', '2021-02-28')
hf_vol_price_factor('2011-01-01', '2021-02-28')
hf_volume_ratio_factor('2011-01-01', '2021-02-28')


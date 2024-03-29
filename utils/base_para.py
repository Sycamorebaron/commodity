import os, sys
from sqlalchemy import create_engine
import pandas as pd
import time

system = sys.platform
if system.startswith('win'):
    local_data_path = r'C:\futures_data'
    local_data_path_5T = r'C:\futures_data_5T'
    local_factor_data_path = r'C:\futures_factor'
    local_hf_factor_path = r'C:\30t_factor'
    local_15t_factor_path = r'C:\15t_factor'
    local_5t_factor_path = r'C:\5t_factor'
    local_1d_factor_path = r'C:\1d_factor'
elif system.startswith('linux'):
    local_data_path = r'/home/sycamore/futures_data'
    local_data_path_5T = r'/home/sycamore/futures_data_5T'
    local_factor_data_path = r'/home/sycamore/futures_factor_1T'
    local_hf_factor_path = r'/home/sycamore/30t_factor'
    local_15t_factor_path = r'/home/sycamore/15t_factor'
    local_5t_factor_path = r'/home/sycamore/5t_factor'
    local_1d_factor_path = r'/home/sycamore/1d_factor'
else:
    local_data_path = ''


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, 'Timer', round(end-start, 4))
        return res
    return wrapper


ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_PATH, 'data')

INPUT_DATA_PATH = os.path.join(DATA_PATH, 'input')
OUTPUT_DATA_PATH = os.path.join(DATA_PATH, 'output')
COMM_FACTOR_DATA_PATH = os.path.join(DATA_PATH, 'comm_factor')
HF_COMM_FACTOR_DATA_PATH = os.path.join(DATA_PATH, 'hf_comm_factor')
F_RTN_DATA_PATH = os.path.join(DATA_PATH, 'f_rtn')
HF_FACTOR_DATA_PATH = os.path.join(DATA_PATH, 'HFfactor')

eg = create_engine('postgresql://postgres:thomas@localhost:5432/commodity')

FULL_CONTRACT_INFO = [
    {'id': 'PB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2011-03-24', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'BU', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-10-09', 'last_de_listed_date': '2021-08-16', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'WR', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2009-03-27', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'FG', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2012-12-03', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'L', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2007-07-31', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'PK', 'month_list': [1, 3, 10, 11, 12], 'first_listed_date': '2021-02-01', 'last_de_listed_date': '2021-12-14', 'init_margin_rate': 0.08, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'JM', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-03-22', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 60.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'UR', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2019-08-09', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SP', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2018-11-27', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'T', 'month_list': [9, 3, 12, 6], 'first_listed_date': '2015-03-20', 'last_de_listed_date': '2021-09-10', 'init_margin_rate': 0.04, 'contract_unit': 10000.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'C', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2004-09-22', 'last_de_listed_date': '2022-01-17', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'M', 'month_list': [1, 3, 5, 7, 8, 9, 11, 12], 'first_listed_date': '2000-07-17', 'last_de_listed_date': '2022-01-17', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'WH', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2012-09-21', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'RU', 'month_list': [1, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'first_listed_date': '1999-01-04', 'last_de_listed_date': '2022-01-17', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SR', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2006-01-06', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SN', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2015-03-27', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 1.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'TC', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-09-26', 'last_de_listed_date': '2016-03-07', 'init_margin_rate': 0.05, 'contract_unit': 200.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SF', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2014-08-08', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'PP', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2014-02-28', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'OI', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2012-09-17', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'AP', 'month_list': [1, 3, 5, 7, 10, 11, 12], 'first_listed_date': '2017-12-22', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.35, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'FB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-12-06', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'A', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2002-03-15', 'last_de_listed_date': '2022-01-17', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'AL', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '1999-01-04', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'CS', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2014-12-19', 'last_de_listed_date': '2022-01-17', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'S', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '1999-01-04', 'last_de_listed_date': '2002-11-14', 'init_margin_rate': 0.05, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'P', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2007-10-29', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SA', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2019-12-06', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'EG', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2018-12-10', 'last_de_listed_date': '2022-01-26', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'TS', 'month_list': [9, 3, 12, 6], 'first_listed_date': '2018-08-17', 'last_de_listed_date': '2021-09-10', 'init_margin_rate': 0.01, 'contract_unit': 20000.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'ZN', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2007-03-26', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'RR', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2019-08-16', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SC', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2018-03-26', 'last_de_listed_date': '2022-01-21', 'init_margin_rate': 0.2, 'contract_unit': 1000.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'CJ', 'month_list': [1, 3, 5, 7, 9, 12], 'first_listed_date': '2019-04-30', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'LH', 'month_list': [9, 11, 1], 'first_listed_date': '2021-01-08', 'last_de_listed_date': '2021-11-25', 'init_margin_rate': 0.15, 'contract_unit': 16.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'V', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2009-05-25', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'MA', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2014-07-15', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'EB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2019-09-26', 'last_de_listed_date': '2022-01-26', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'TF', 'month_list': [9, 3, 12, 6], 'first_listed_date': '2013-09-06', 'last_de_listed_date': '2021-09-10', 'init_margin_rate': 0.03, 'contract_unit': 10000.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'RI', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2012-09-21', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'I', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-10-18', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 100.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SS', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2019-09-25', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'B', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2004-12-22', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'LR', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2014-07-08', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'AG', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2012-05-10', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 15.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'CF', 'month_list': [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2004-06-01', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'RS', 'month_list': [8, 9, 11, 7], 'first_listed_date': '2012-12-28', 'last_de_listed_date': '2021-09-14', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'HC', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2014-03-21', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'ME', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2011-10-28', 'last_de_listed_date': '2015-04-15', 'init_margin_rate': 0.06, 'contract_unit': 50.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'WS', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2003-03-28', 'last_de_listed_date': '2013-03-21', 'init_margin_rate': 0.05, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'WT', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '1999-01-04', 'last_de_listed_date': '2012-09-20', 'init_margin_rate': 0.05, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'NR', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2019-08-12', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'JR', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2013-11-18', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'FU', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2004-08-25', 'last_de_listed_date': '2022-01-21', 'init_margin_rate': 0.4, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'PM', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2012-03-23', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 50.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'RO', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2007-06-08', 'last_de_listed_date': '2013-03-14', 'init_margin_rate': 0.05, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'BC', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2020-11-19', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'PG', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2020-03-30', 'last_de_listed_date': '2022-01-26', 'init_margin_rate': 0.2, 'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'SM', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2014-08-08', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'LU', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2020-06-22', 'last_de_listed_date': '2022-01-21', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'RB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2009-03-27', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'ER', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2009-04-20', 'last_de_listed_date': '2013-03-21', 'init_margin_rate': 0.05, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'J', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2011-04-15', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.2, 'contract_unit': 100.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'CU', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '1999-01-04', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'RM', 'month_list': [1, 3, 5, 7, 8, 9, 11], 'first_listed_date': '2012-12-28', 'last_de_listed_date': '2022-01-14', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'AU', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2008-01-09', 'last_de_listed_date': '2021-05-17', 'init_margin_rate': 0.2, 'contract_unit': 1000.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'Y', 'month_list': [1, 3, 5, 7, 8, 9, 11, 12], 'first_listed_date': '2006-01-09', 'last_de_listed_date': '2022-01-17', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'PF', 'month_list': [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2020-10-12', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.07, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'CY', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2017-08-18', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.2, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'JD', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-11-08', 'last_de_listed_date': '2022-01-26', 'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'ZC', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2015-06-08', 'last_de_listed_date': '2022-02-07', 'init_margin_rate': 0.2, 'contract_unit': 100.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'TA', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2006-12-18', 'last_de_listed_date': '2022-02-14', 'init_margin_rate': 0.3, 'contract_unit': 5.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'BB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-12-06', 'last_de_listed_date': '2022-02-21', 'init_margin_rate': 0.4, 'contract_unit': 500.0, 'open_comm': 5, 'close_comm': 5},
    {'id': 'NI', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2015-03-27', 'last_de_listed_date': '2022-02-15', 'init_margin_rate': 0.2, 'contract_unit': 1.0, 'open_comm': 5, 'close_comm': 5}
]


DEAD_CONTRACT_INFO = \
    [
        {'id': 'WH', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2012-07-24', 'init_margin_rate': 0.2,
         'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'B', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2004-12-22',
         'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'FU', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2004-08-25',
         'init_margin_rate': 0.4, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'RS', 'month_list': [8, 9, 11, 7], 'first_listed_date': '2012-12-28', 'init_margin_rate': 0.2,
         'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'PM', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2012-01-17', 'init_margin_rate': 0.2,
         'contract_unit': 50.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'LR', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2014-07-08', 'init_margin_rate': 0.2,
         'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'BB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-12-06',
         'init_margin_rate': 0.4, 'contract_unit': 500.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'JR', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2013-11-18', 'init_margin_rate': 0.2,
         'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'RI', 'month_list': [1, 3, 5, 7, 9, 11], 'first_listed_date': '2012-07-24', 'init_margin_rate': 0.2,
         'contract_unit': 20.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'FB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2013-12-06',
         'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
        {'id': 'WR', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2009-03-27',
         'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5},
    ]

ABO_LIST = [
    'BB', 'IF', 'IH', 'IC', 'JR', 'LR', 'PM', 'RI', 'RR', 'RS', 'T', 'TS', 'TF', 'WH', 'WR', 'WS', 'WT', 'S', 'FU', 'B'
]
DATA_CORRUPTED_LIST = [pd.to_datetime('2010-12-20')]

NORMAL_CONTRACT_INFO = [
    i for i in FULL_CONTRACT_INFO if i['id'] not in ABO_LIST + DATA_CORRUPTED_LIST
]

JUMP_DATE = [pd.to_datetime]

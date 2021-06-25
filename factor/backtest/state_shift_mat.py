import sys
import os
import pandas as pd
from dateutil.relativedelta import relativedelta
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.backtest.factor_test import BackTest
from factor.backtest.syn_test_hf import HFSynTest
from utils.base_para import local_data_path, local_15t_factor_path, NORMAL_CONTRACT_INFO

pd.set_option('expand_frame_repr', False)
# pd.set_option('display.max_rows', 200)

class StateShiftMat(HFSynTest):

    def __init__(
        self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
        term, leverage, train_data_len
    ):
        BackTest.__init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage,
            night=False
        )
        self.open_comm = []
        self.train_data_len = train_data_len
        self.state_shift_mat_list = []


    def cal_state_shift_mat(self, comm, now_date, use_days=30):
        data = self.exchange.contract_dict[comm].data_dict[
            self.exchange.contract_dict[comm].operate_contract
        ]
        data = data.loc[
            (data['datetime'] < now_date) &
            (data['datetime'] >= now_date - relativedelta(days=use_days))
        ].copy().reset_index(drop=True)

        # 去掉一些开盘时间
        data = data.loc[data['datetime'].apply(lambda x: x.strftime('%H:%M') not in ['09:01', '13:31', '21:01'])]

        """     
                this term
              neg  neu  pos
        [[neg   x    x    x  ],       
         [neu   x    x    x  ],
         [pos   x    x    x  ]]
        """
        if len(data):

            neg_neg = len(data.loc[(data['label'] == -1) & (data['label'].shift(1) == -1)])  # [0][0]
            neg_neu = len(data.loc[(data['label'] == 0) & (data['label'].shift(1) == -1)])  # [0][1]
            neg_pos = len(data.loc[(data['label'] == 1) & (data['label'].shift(1) == -1)])  # [0][2]

            neu_neg = len(data.loc[(data['label'] == -1) & (data['label'].shift(1) == 0)])  # [1][0]
            neu_neu = len(data.loc[(data['label'] == 0) & (data['label'].shift(1) == 0)])  # [1][1]
            neu_pos = len(data.loc[(data['label'] == 1) & (data['label'].shift(1) == 0)])  # [1][2]

            pos_neg = len(data.loc[(data['label'] == -1) & (data['label'].shift(1) == 1)])  # [2][0]
            pos_neu = len(data.loc[(data['label'] == 0) & (data['label'].shift(1) == 1)])  # [2][1]
            pos_pos = len(data.loc[(data['label'] == 1) & (data['label'].shift(1) == 1)])  # [2][2]

            return [
                [neg_neg / len(data), neg_neu / len(data), neg_pos / len(data)],
                [neu_neg / len(data), neu_neu / len(data), neu_pos / len(data)],
                [pos_neg / len(data), pos_neu / len(data), pos_pos / len(data)],
            ]
        else:
            return [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def _daily_process(self):
        self.open_comm = self._open_comm()

        print(self.agent.earth_calender.now_date)

        for comm in self.exchange.contract_dict.keys():
            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            self.exchange.contract_dict[comm].renew_main_sec_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            print(self.exchange.contract_dict[comm].operate_contract)

            for contract in self.exchange.contract_dict[comm].data_dict.keys():
                self.exchange.contract_dict[comm].data_dict[contract]['rtn'] = \
                    self.exchange.contract_dict[comm].data_dict[contract]['close'] / \
                    self.exchange.contract_dict[comm].data_dict[contract]['open'] - 1

                self.exchange.contract_dict[comm].data_dict[contract]['label'] = 0
                self.exchange.contract_dict[comm].data_dict[contract].loc[
                    self.exchange.contract_dict[comm].data_dict[contract]['rtn'] > 0.001,  'label'
                ] = 1
                self.exchange.contract_dict[comm].data_dict[contract].loc[
                    self.exchange.contract_dict[comm].data_dict[contract]['rtn'] < -0.001,  'label'
                ] = -1

        t_state_shift_mat = {'date': self.agent.earth_calender.now_date.strftime('%Y-%m-%d')}
        for comm in self.open_comm:
            state_shift_mat = self.cal_state_shift_mat(
                comm=comm, now_date=self.agent.earth_calender.now_date
            )
            t_state_shift_mat[comm] = state_shift_mat
        self.state_shift_mat_list.append(t_state_shift_mat)

        if self.agent.earth_calender.now_date.strftime('%m') == '12':

            res = json.dumps(self.state_shift_mat_list)
            f = open('D:\commodity\data\state_shift_mat.json', 'w')
            f.write(res)
            f.close()


if __name__ == '__main__':

    syn_test = StateShiftMat(
        factor_name='hf_syn',
        begin_date='2011-06-11',
        end_date='2021-02-28',
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['PB', 'L', 'C', 'M', 'RU', 'SR', 'A']],
        contract_list=NORMAL_CONTRACT_INFO,
        local_factor_data_path=local_15t_factor_path,
        local_data_path=local_data_path,
        term='15T',
        leverage=False,
        train_data_len=100
    )
    syn_test.test()

    res = json.dumps(syn_test.state_shift_mat_list)
    f = open('D:\commodity\data\state_shift_mat.json', 'w')
    f.write(res)
    f.close()
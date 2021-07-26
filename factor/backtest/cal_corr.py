import sys
import os
from datetime import timedelta
from multiprocessing import Pool
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.test.main_test import MainTest
from utils.base_para import *

class BackTest(MainTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage,
                 night):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, leverage)
        self.term = term
        self.term_list = self._gen_term_list(term=term, night=night)

    def _last_dt(self, now_dt):
        """
        找到用于计算因子的数据开始时间
        :param now_dt:
        :return:
        """
        if pd.to_datetime(now_dt).strftime('%H:%M') != '09:01':
            return '%s %s:00' % (
                pd.to_datetime(now_dt).strftime('%Y-%m-%d'),
                self.term_list[self.term_list.index(pd.to_datetime(now_dt).strftime('%H:%M')) - 1]
            )
        else:
            return '%s %s:00' % (
                (self.exchange.trade_calender.get_last_trading_date(
                    date=self.agent.earth_calender.now_date
                )).strftime('%Y-%m-%d'),
                self.term_list[-1]
            )

    def _get_cal_factor_data(self, comm, now_dt, last_dt):
        """
        找到用于计算因子的数据
        :param comm:
        :param now_dt:
        :param last_dt:
        :return:
        """

        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        cond1 = data['datetime'] >= last_dt
        cond2 = data['datetime'] < now_dt
        cal_factor_data = data.loc[cond1 & cond2].reset_index(drop=True)

        return cal_factor_data

    @staticmethod
    def _gen_term_list(term, night):
        if not night:
            begin_time = pd.to_datetime('2000-01-01 09:01')
            end_time = pd.to_datetime('2000-01-01 15:00')
            rest_time_begin_1 = pd.to_datetime('2000-01-01 10:15')
            rest_time_end_1 = pd.to_datetime('2000-01-01 10:30')
            rest_time_begin_2 = pd.to_datetime('2000-01-01 11:30')
            rest_time_end_2 = pd.to_datetime('2000-01-01 13:30')

            now_term_begin = begin_time
            term_list = []
            if term.endswith('T'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                        ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                        (now_term_begin > rest_time_end_2):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(minutes=int(term.strip('T')))
            elif term.endswith('H'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                        ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                        (now_term_begin > rest_time_end_2):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(hours=int(term.strip('H')))
            else:
                raise Exception('TERM NOT SUPPORT')
        else:

            begin_time = pd.to_datetime('2000-01-01 09:01')
            end_time = pd.to_datetime('2000-01-01 23:00')
            rest_time_begin_1 = pd.to_datetime('2000-01-01 10:15')
            rest_time_end_1 = pd.to_datetime('2000-01-01 10:30')

            rest_time_begin_2 = pd.to_datetime('2000-01-01 11:30')
            rest_time_end_2 = pd.to_datetime('2000-01-01 13:30')

            rest_time_begin_3 = pd.to_datetime('2000-01-01 15:00')
            rest_time_end_3 = pd.to_datetime('2000-01-01 21:00')

            now_term_begin = begin_time
            term_list = []
            if term.endswith('T'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                        ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                        (now_term_begin > rest_time_end_2) & (now_term_begin < rest_time_begin_3) or \
                        (now_term_begin > rest_time_end_3):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(minutes=int(term.strip('T')))
            elif term.endswith('H'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                        ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                        (now_term_begin > rest_time_end_2) & (now_term_begin < rest_time_begin_3) or \
                        (now_term_begin > rest_time_end_3):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(hours=int(term.strip('H')))

        return term_list

    def clear_position(self, term_begin_time):
        close_pos = {}
        for comm in self.exchange.account.position.holding_position.keys():
            for contract in self.exchange.account.position.holding_position[comm].keys():
                close_pos[contract] = 0
        if len(close_pos):
            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
            )
            self.exchange.account.equity = self.exchange.account.cash
            self.agent.recorder.record_trade(info=close_trade_info)

    def strategy_target_pos(self, now_dt):
        """
        target pos中要包含现有持仓平仓的 position
        target_pos = {'L2005': 0.5, 'FG2005': -0.5}
        :param now_dt:
        :return:
        """
        return {'L2005': 0.5, 'FG2005': -0.5}

    def _termly_process(self, term_begin_time):
        """
        每期进行的流程
        :param term_begin_time:
        :return:
        """
        # print('$' * 25, term_begin_time, '$' * 25)
        # print('-' * 25, 'before change position', '-' * 25)
        # print('CASH', self.exchange.account.cash)
        # print('position\n', self.exchange.account.position.holding_position)
        # print('-' * 70)

        # 先平仓
        close_pos = {}
        for comm in self.exchange.account.position.holding_position.keys():
            for contract in self.exchange.account.position.holding_position[comm].keys():
                close_pos[contract] = 0
        if len(close_pos):
            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='close'
            )
            self.exchange.account.equity = self.exchange.account.cash
            # self.agent.recorder.record_trade(info=close_trade_info)

        # 再开仓
        target_pos = self.strategy_target_pos(
            now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
        )

        # 根据目标仓位调仓
        open_trade_info = self.agent.change_position(
            exchange=self.exchange,
            target_pos=target_pos,
            now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
            field='open'
        )

        # 记录交易
        # self.agent.recorder.record_trade(info=open_trade_info)

    def _termly_process_skip_rest(self, term_begin_time):
        """
        每期进行的流程
        :param term_begin_time:
        :return:
        """
        # print('$' * 25, term_begin_time, '$' * 25)
        # print('-' * 25, 'before change position', '-' * 25)
        # print('CASH', self.exchange.account.cash)
        # print('position\n', self.exchange.account.position.holding_position)
        # print('-' * 70)

        # 先平仓
        close_pos = {}
        for comm in self.exchange.account.position.holding_position.keys():
            for contract in self.exchange.account.position.holding_position[comm].keys():
                close_pos[contract] = 0

        if len(close_pos):
            print('close', term_begin_time)
            last_end_time = pd.to_datetime(self._last_dt(now_dt=term_begin_time)) + timedelta(
                minutes=int(self.term[:-1]) - 1)

            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='close',
            )
            self.exchange.account.equity = self.exchange.account.cash
            self.agent.recorder.record_trade(info=close_trade_info)

        # if term_begin_time not in ['10:01', '10:31']:
        # if term_begin_time not in ['09:01', '09:16', '10:01', '10:16', '10:31', '13:01', '21:01']:
        if term_begin_time not in ['09:01', '10:16', '13:31', '21:01']:
            # 再开仓
            target_pos = self.strategy_target_pos(
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
            )

            # 根据目标仓位调仓
            open_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=target_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='open'
            )

            # 记录交易
            self.agent.recorder.record_trade(info=open_trade_info)
            # print('-' * 25, 'after change position', '-' * 25)
            # print('CASH', self.exchange.account.cash)
            # print('position\n',self.exchange.account.position.holding_position)
            # print('-' * 70)
            # print('$' * 55)

    def _daily_process(self):
        """
        每日进行的流程
        :return:
        """
        print(self.agent.earth_calender.now_date)

        for comm in self.exchange.contract_dict.keys():
            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue
            print(comm)

            self.exchange.contract_dict[comm].renew_main_sec_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

        # 逐期遍历
        for term_begin_time in self.term_list:
            self._termly_process(term_begin_time=term_begin_time)

        # 每日清仓，只需要平仓手上的仓位
        self.clear_position(term_begin_time=self.term_list[-1])

        # 记录资金情况
        self.agent.recorder.record_equity(
            info={
                'date': self.agent.earth_calender.now_date,
                'equity': self.exchange.account.equity,
            }
        )

        print('*' * 30)
        print('DATE', self.agent.earth_calender.now_date)
        print('EQUITY', self.exchange.account.equity)
        print('*' * 30)
        print('=' * 50)


def _corr_task(hist_factor_comm, comm):
    segs = 10

    hist_rtn_df = pd.DataFrame(hist_factor_comm)
    hist_rtn_df['f_rtn'] = hist_rtn_df['rtn'].shift(-1)

    if len(hist_rtn_df) < (segs * 30) + 1:
        return {comm: None}
    if not abs(hist_factor_comm[-1]['factor']) > 0:
        return {comm: None}

    # 去掉其中factor为nan的部分
    hist_rtn_df = hist_rtn_df.loc[hist_rtn_df['factor'].notna()].reset_index(drop=True)

    # 去掉之后也要保证有一定的数据量
    if len(hist_rtn_df) < (segs * 30) + 1:
        return {comm: None}

    hist_rtn_df = hist_rtn_df[-301:]

    train_df = hist_rtn_df[:-1]
    corr = train_df['factor'].corr(train_df['f_rtn'])
    return {comm: corr}


class CalCorrBackTest(BackTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night):
        BackTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night)
        self.hist_factor = {}
        self.hist_corr = []

    def _get_cal_factor_data(self, comm, now_dt, last_dt):
        op_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        d = self.exchange.contract_dict[comm].data_dict[op_contract].copy()
        d = d.loc[d['datetime'] < now_dt][-15:].reset_index(drop=True)
        rtn = d['close'].iloc[-1] / d['open'].iloc[0] - 1
        d['rtn'] = d['close'] / d['open'] - 1
        d['dvol'] = d['volume'] - d['volume'].shift(1)

        d['dvol'] = d['dvol'].astype(float)
        d['rtn'] = d['rtn'].astype(float)
        corr = d['rtn'].corr(d['dvol'])

        if comm in self.hist_factor.keys():
            self.hist_factor[comm].append(
                {
                    'candle_begin_time': d['datetime'].iloc[0] - timedelta(minutes=1),
                    'contract': op_contract,
                    'factor': corr,
                    'rtn': rtn,
                }
            )
        else:
            self.hist_factor[comm] = [
                {
                    'candle_begin_time': d['datetime'].iloc[0] - timedelta(minutes=1),
                    'contract': op_contract,
                    'factor': corr,
                    'rtn': rtn,
                }
            ]

    def strategy_target_pos(self, now_dt):
        _t_corr = {'datetime': now_dt}

        pool = Pool(processes=4)
        result = []
        for comm in self.exchange.contract_dict.keys():
            if (pd.to_datetime(now_dt) < self.exchange.contract_dict[comm].first_listed_date + timedelta(days=2)) or \
                    (pd.to_datetime(now_dt) > self.exchange.contract_dict[comm].last_de_listed_date):
                continue
            self._get_cal_factor_data(
                comm=comm, now_dt=now_dt, last_dt=self._last_dt(now_dt=now_dt)
            )
            hist_factor_comm = self.hist_factor[comm]
            result.append(pool.apply_async(func=_corr_task, args=(hist_factor_comm, comm,)))

        pool.close()
        pool.join()

        if len(result):
            for i in result:
                _r = i.get()
                _t_corr = {**_t_corr, **i.get()}
        print(_t_corr)
        #
        #
        # # ====== 计算相关系数，保存下来看范围====
        #     _t_corr[comm] = corr
        #
        # self.hist_corr.append(_t_corr)
        #
        return {}

    def _termly_process_skip_rest(self, term_begin_time):
        """
        每期进行的流程
        :param term_begin_time:
        :return:
        """

        # 先平仓
        close_pos = {}
        for comm in self.exchange.account.position.holding_position.keys():
            for contract in self.exchange.account.position.holding_position[comm].keys():
                close_pos[contract] = 0

        if len(close_pos):
            print('close', term_begin_time)
            last_end_time = pd.to_datetime(self._last_dt(now_dt=term_begin_time)) + timedelta(
                minutes=int(self.term[:-1]) - 1)

            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='close',
            )
            self.exchange.account.equity = self.exchange.account.cash
            self.agent.recorder.record_trade(info=close_trade_info)

        # if term_begin_time not in ['10:01', '10:31']:
        # if term_begin_time not in ['09:01', '09:16', '10:01', '10:16', '10:31', '13:01', '21:01']:
        if term_begin_time not in ['09:01', '10:16', '13:31', '21:01']:
            # 再开仓
            target_pos = self.strategy_target_pos(
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
            )

    def _termly_process(self, term_begin_time):
        BackTest._termly_process_skip_rest(self, term_begin_time)
        print('cumulated fee', self.agent.trade_center.cumulated_fee)


if __name__ == '__main__':


    back_test = CalCorrBackTest(
        test_name='moment',
        begin_date='2014-01-01',
        end_date='2020-12-31',
        init_cash=10000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path,
        term='15T',
        leverage=False,
        night=False
    )
    back_test.test()
    corr_df = pd.DataFrame(back_test.hist_corr)
    corr_df.to_csv(r'D:\commodity\data\hist_corr\dvol_rtn.csv')
    # back_test.agent.recorder.equity_curve().to_csv(r'C:\Users\sycam\Desktop\corr_reverse.csv')
    # back_test.agent.recorder.trade_hist().to_csv(r'C:\Users\sycam\Desktop\corr_reverse_trade_hist.csv')
    # back_test.agent.recorder.trade_hist().to_csv(r'C:\Users\sycam\Desktop\momentum.csv')

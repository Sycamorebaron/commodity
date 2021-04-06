from factor.test.main_test import MainTest
from utils.base_para import *
from dateutil.relativedelta import relativedelta
import pandas as pd
from sklearn.cluster import KMeans

pd.set_option('expand_frame_repr', False)


class FactorTest(MainTest):
    def _daily_process(self):
        pass

    def test(self):
        while not self.agent.earth_calender.end_of_test():
            # 交易日
            if self.exchange.trade_calender.tradable_date(date=self.agent.earth_calender.now_date):
                self._daily_process()
            self.agent.earth_calender.next_day()


class Cluster(FactorTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, cluster_months):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list)
        self.cluster_months = cluster_months

    def _daily_process(self):
        print('=== %s ===' % self.agent.earth_calender.now_date.strftime('%Y-%m-%d'))
        print('renew contract...')
        for contract in self.exchange.contract_dict.keys():
            if self.agent.earth_calender.now_date < \
                    self.exchange.contract_dict[contract].first_listed_date + relativedelta(months=1):
                continue

            self.exchange.contract_dict[contract].renew_open_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[contract].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

        # 每个月测试一次
        if self.exchange.trade_calender.if_first_trading_date_monthly(
            date=self.agent.earth_calender.now_date
        ):
            last_month_first_date = self.exchange.trade_calender.get_monthly_first_trading_date(
                month=(self.agent.earth_calender.now_date - relativedelta(months=self.cluster_months)).strftime('%Y-%m')
            )

            print(last_month_first_date, self.agent.earth_calender.now_date)

            cluster_res = self.k_means_cluster(
                data_begin_date=last_month_first_date,
                data_end_date=self.agent.earth_calender.now_date
            )
            print(cluster_res)
        print('=========')

    def k_means_cluster(self, data_begin_date, data_end_date):
        """
        截取数据，使用收益率进行聚类
        :param data_begin_date:
        :param data_end_date:
        :return:
        """
        feasible_commodity = []
        for commodity in self.exchange.contract_dict.keys():
            if self.agent.earth_calender.now_date < \
                    self.exchange.contract_dict[commodity].first_listed_date + relativedelta(months=self.cluster_months):
                continue
            else:
                feasible_commodity.append(commodity)
        print(feasible_commodity)

        cluster_data_set = pd.DataFrame()
        for comm in feasible_commodity:
            data = self.exchange.contract_dict[comm].data_dict[
                self.exchange.contract_dict[comm].operate_contract
            ]

            cond1 = data['datetime'] < data_end_date
            cond2 = data['datetime'] >= data_begin_date
            data = data.loc[cond1 & cond2, ['datetime', 'close']]

            data = data.resample(on='datetime', rule='1D').agg(
                {
                    'close': 'last'
                }
            )
            data.reset_index(inplace=True)
            data.columns = ['datetime', comm]
            if len(cluster_data_set):
                cluster_data_set = cluster_data_set.merge(data, how='outer', on='datetime')
            else:
                cluster_data_set = data
        cluster_data_set.dropna(axis=0, inplace=True, how='any')

        for comm in cluster_data_set.columns[1:]:
            cluster_data_set['%s_rtn' % comm] = cluster_data_set[comm] / cluster_data_set[comm].shift(1) - 1
            cluster_data_set.drop(comm, axis=1, inplace=True)

        cluster_data_set = cluster_data_set[1:].reset_index(drop=True)
        cluster_data_set = cluster_data_set[cluster_data_set.columns[1:]].T
        model = KMeans(n_clusters=4)
        cluster_data_set['cata'] = model.fit_predict(X=cluster_data_set[cluster_data_set.columns])
        cluster_res = dict(cluster_data_set['cata'])
        return cluster_res


class SingleCommTest(FactorTest):
    def _daily_process(self):
        print('=== %s ===' % self.agent.earth_calender.now_date.strftime('%Y-%m-%d'))
        print('renew contract...')
        for contract in self.exchange.contract_dict.keys():
            if self.agent.earth_calender.now_date < \
                    self.exchange.contract_dict[contract].first_listed_date + relativedelta(months=1):
                continue

            self.exchange.contract_dict[contract].renew_open_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[contract].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

            print(self.exchange.contract_dict[contract].data_dict)
            exit()







if __name__ == '__main__':
    # factor_test = Cluster(
    #     test_name='cluster_test',
    #     begin_date='2011-01-01',
    #     end_date='2020-12-31',
    #     init_cash=10000000,
    #     contract_list=FULL_CONTRACT_INFO,
    #     cluster_months=2
    # )
    #
    # factor_test.test()

    single_comm_test = SingleCommTest(
        test_name='cluster_test',
        begin_date='2011-01-01',
        end_date='2020-12-31',
        init_cash=10000000,
        contract_list=[
            {
                'id': 'RB', 'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'first_listed_date': '2009-03-27',
                'init_margin_rate': 0.2, 'contract_unit': 10.0, 'open_comm': 5, 'close_comm': 5
            }
        ]
    )
    single_comm_test.test()

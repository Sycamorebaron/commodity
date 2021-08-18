import sys
import os
import pandas as pd
import time
import warnings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from genetic_algo.program.data_former import DataFormer
from genetic_algo.program.pre_procsess import PreProcess
from genetic_algo.gplearn.genetic import SymbolicRegressor
from gplearn.genetic import SymbolicRegressor as SR

warnings.filterwarnings('ignore')

pd.set_option('expand_frame_repr', False)


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, 'Timer', round(end-start, 4))
        return res
    return wrapper


class CommGenetic:
    def __init__(self, comm):
        self.data_former = DataFormer(comm=comm)
        self.pre_process = PreProcess()
        self.res = {}

    @timer
    def train(self, train_len):
        data = self.data_former.dropna_data
        data = data[[i for i in data.columns if i not in ['datetime']]]
        data = self.pre_process.stationalize(data, targets=[i for i in data.columns if i not in ['f_rtn']])

        train_data = data[:train_len].reset_index(drop=True)
        test_data = data[train_len:].reset_index(drop=True)

        base_f = [i for i in data.columns if i not in ['f_rtn']]

        # base_f = ['d_open', 'd_high', 'd_low', 'd_close', 'd_vol', 'd_oi']
        target = 'f_rtn'

        model_gp = SymbolicRegressor(
            generations=3,  # 公式进化的世代数量。世代数量越多，消耗算力越多，公式的进化次数越多。
            population_size=1000,  # 每一代公式群体中的公式数量。公式数量越大，消耗算力越多，公式之间组合的空间越大。
            function_set=(
                'add', 'sub', 'mul', 'div', 'sqrt', 'log', 'abs', 'neg', 'inv', 'max', 'min', 'sin', 'cos', 'tan',
                'rank', 'delay_5', 'delay_10', 'delay_15', 'delay_20', 'ts_corr_5', 'ts_corr_10', 'ts_corr_15',
                'ts_corr_20', 'ts_cov_5', 'ts_cov_10', 'ts_cov_15', 'ts_cov_20', 'scale_1', 'scale_2', 'scale_3',
                'scale_4', 'delta_1', 'delta_2', 'delta_3', 'delta_4', 'signedpower_2', 'signedpower_3',
                'signedpower_4', 'signedpower_5', 'decay_linear_5', 'decay_linear_10', 'decay_linear_15',
                'decay_linear_20', 'ts_min_5', 'ts_min_10', 'ts_min_15', 'ts_min_20', 'ts_max_5', 'ts_max_10',
                'ts_max_15', 'ts_max_20', 'ts_argmin_5', 'ts_argmin_10', 'ts_argmin_15', 'ts_argmin_20', 'ts_argmax_5',
                'ts_argmax_10', 'ts_argmax_15', 'ts_argmax_20', 'ts_rank_5', 'ts_rank_10', 'ts_rank_15', 'ts_rank_20',
                'ts_sum_5', 'ts_sum_10', 'ts_sum_15', 'ts_sum_20', 'ts_prod_5', 'ts_prod_10', 'ts_prod_15',
                'ts_prod_20', 'ts_stddev_5', 'ts_stddev_10', 'ts_stddev_15', 'ts_stddev_20', 'ts_zscore_5',
                'ts_zscore_10', 'ts_zscore_15', 'ts_zscore_20', 'rank_sub', 'rank_div', 'sigmoid'
            ),  # 用于构建和进化公式时使用的函数集，可自定义更多函数。
            init_depth=(1, 4),  # 公式树的初始化深度，init_depth是一个二元组(min_depth,max_depth)，树的初始深度将处在
                                # [min_depth, max_depth]区间内。设置树深度最小1层，最大4层。最大深度越深，可能得出越复杂的因子，
                                # 但是因子的意义更难解释。
            tournament_size=20,  # 每一代的所有公式中，tournament_size个公式会被随机选中，其中适应度最高的公式能进行变异或繁殖生
                                 # 成下一代公式。tournament_size越小，随机选择范围越小，选择的结果越不确定.
            metric='pearson',  # 适应度指标，可自定义更多指标。
            p_crossover=0.5,  # 父代进行交叉变异进化的概率。交叉变异是最有效的进化方式，可以设置为较大概率。
            p_subtree_mutation=0.01,  # 父代进行子树变异进化的概率。子树变异的结果不稳定，概率不宜过大。
            p_hoist_mutation=0,  # 父代进行Hoist变异进化的概率。本文的测试中公式树层次都较低，所以没有使用Hoist变异。
            p_point_mutation=0.01,  # 父代进行点变异进化的概率。点变异的结果不稳定，概率不宜过大。
            p_point_replace=0.4,  # 即点变异中父代每个节点进行变异进化的概率。点变异的概率已经很小，可设置为较大概率保证点变异的执行
        )

        X_train = train_data[base_f]
        y_train = train_data[target]

        X_test = test_data[base_f]
        y_test = pd.DataFrame(test_data[target])

        model_gp.fit(X_train, y_train)
        y_test_pred = model_gp.predict(X=X_test)
        y_test['pred'] = pd.Series(y_test_pred)

        print(model_gp._program, y_test['f_rtn'].corr(y_test['pred']))

        self.res[str(model_gp._program)] = y_test['f_rtn'].corr(y_test['pred'])


if __name__ == '__main__':
    comm = 'FG'
    comm_genetic = CommGenetic(comm=comm)
    for i in range(50):
        print(i, '-' * 50)
        comm_genetic.train(train_len=1000)
    res_df = pd.DataFrame(comm_genetic.res, index=['corr']).T
    res_df.to_csv(r'D:\commodity\genetic_algo\data\%sres_df.csv' % comm)

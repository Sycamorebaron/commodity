# -*- coding: utf-8 -*-
import numpy as np
import geatpy as ea
import math
import time
import pandas as pd
import multiprocessing as mp
from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
from dateutil.relativedelta import relativedelta

warnings.filterwarnings("ignore")
pd.set_option('mode.chained_assignment', None)


# ------------定义目标函数
# 带止损的布林线策略
def signal_bolling_with_stop_lose(df, para=[100, 2, 5]):
    """
    布林线中轨：n天收盘价的移动平均线
    布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
    布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
    当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过下轨的时候，平仓。
    当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过上轨的时候，平仓。

    另外，当价格往亏损方向超过百分之stop_lose的时候，平仓止损。
    :param df:  原始数据
    :param para:  参数，[n, m, stop_lose]
    :return:
    """

    df.sort_values(by='candle_begin_time', inplace=True)
    # ===计算指标
    n = int(para[0])
    m = para[1]
    stop_loss_pct = para[2]
    trade_count = 0
    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()

    # 计算上轨、下轨道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=1)  # ddof代表标准差自由度
    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']

    # ===找出做多信号
    condition1 = df['close'] > df['upper']  # 当前K线的收盘价 > 上轨
    condition2 = df['close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多
    trade_count += df['signal_long'].sum()
    # ===找出做多平仓信号
    condition1 = df['close'] < df['median']  # 当前K线的收盘价 < 中轨
    condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # ===找出做空信号
    condition1 = df['close'] < df['lower']  # 当前K线的收盘价 < 下轨
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空
    trade_count -= df['signal_short'].sum()

    # ===找出做空平仓信号
    condition1 = df['close'] > df['median']  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= df['median'].shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    df['signal'] = np.nan

    df = df[df['candle_begin_time'] >= pd.to_datetime(df.at[0, 'candle_begin_time'] + relativedelta(days=30))]
    df.reset_index(inplace=True, drop=True)

    # ===考察是否需要止盈止损
    info_dict = {'pre_signal': 0, 'stop_lose_price': None}  # 用于记录之前交易信号，以及止损价格

    # 逐行遍历df，考察每一行的交易信号
    for i in range(df.shape[0]):
        # 如果之前是空仓
        if info_dict['pre_signal'] == 0:
            # 当本周期有做多信号
            if df.at[i, 'signal_long'] == 1:
                df.at[i, 'signal'] = 1  # 将真实信号设置为1
                # 记录当前状态
                pre_signal = 1  # 信号
                stop_lose_price = df.at[i, 'close'] * (
                    1 - stop_loss_pct / 100)  # 以本周期的收盘价乘以一定比例作为止损价格。也可以用下周期的开盘价df.at[i+1, 'open']，但是此时需要注意i等于最后一个i时，取i+1会报错
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}
            # 当本周期有做空信号
            elif df.at[i, 'signal_short'] == -1:
                df.at[i, 'signal'] = -1  # 将真实信号设置为-1
                # 记录相关信息
                pre_signal = -1  # 信号
                stop_lose_price = df.at[i, 'close'] * (
                    1 + stop_loss_pct / 100)  # 以本周期的收盘价乘以一定比例作为止损价格，也可以用下周期的开盘价df.at[i+1, 'open']
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}
            # 无信号
            else:
                # 记录相关信息
                info_dict = {'pre_signal': 0, 'stop_lose_price': None}

        # 如果之前是多头仓位
        elif info_dict['pre_signal'] == 1:
            # 当本周期有平多仓信号，或者需要止损
            if (df.at[i, 'signal_long'] == 0) or (df.at[i, 'close'] < info_dict['stop_lose_price']):
                df.at[i, 'signal'] = 0  # 将真实信号设置为0
                # 记录相关信息
                info_dict = {'pre_signal': 0, 'stop_lose_price': None}

            # 当本周期有平多仓并且还要开空仓
            if df.at[i, 'signal_short'] == -1:
                df.at[i, 'signal'] = -1  # 将真实信号设置为-1
                # 记录相关信息
                pre_signal = -1  # 信号
                stop_lose_price = df.at[i, 'close'] * (
                    1 + stop_loss_pct / 100)  # 以本周期的收盘价乘以一定比例作为止损价格，也可以用下周期的开盘价df.at[i+1, 'open']
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}

        # 如果之前是空头仓位
        elif info_dict['pre_signal'] == -1:
            # 当本周期有平空仓信号，或者需要止损
            if (df.at[i, 'signal_short'] == 0) or (df.at[i, 'close'] > info_dict['stop_lose_price']):
                df.at[i, 'signal'] = 0  # 将真实信号设置为0
                # 记录相关信息
                info_dict = {'pre_signal': 0, 'stop_lose_price': None}

            # 当本周期有平空仓并且还要开多仓
            if df.at[i, 'signal_long'] == 1:
                df.at[i, 'signal'] = 1  # 将真实信号设置为1
                # 记录相关信息
                pre_signal = 1  # 信号
                stop_lose_price = df.at[i, 'close'] * (
                    1 - stop_loss_pct / 100)  # 以本周期的收盘价乘以一定比例作为止损价格，也可以用下周期的开盘价df.at[i+1, 'open']
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}

        # 其他情况
        else:
            raise ValueError('不可能出现其他的情况，如果出现，说明代码逻辑有误，报错')

    # 将无关的变量删除
    # df.drop(['median', 'std', 'upper', 'lower', 'signal_long', 'signal_short'], axis=1, inplace=True)

    # ===由signal计算出实际的每天持有仓位
    # signal的计算运用了收盘价，是每根K线收盘之后产生的信号，到第二根开盘的时候才买入，仓位才会改变。
    df['pos'] = df['signal'].shift()
    df['pos'].fillna(method='ffill', inplace=True)
    df['pos'].fillna(value=0, inplace=True)  # 将初始行数的position补全为0

    return df, trade_count


# 计算最大回撤
def my_cal_mdd(df, col):
    df_temp = df.copy()
    df_temp['max2here'] = df_temp[col].expanding().max()
    df_temp['dd2here'] = df_temp[col] / df_temp['max2here'] - 1
    max_dd = -df_temp['dd2here'].min()
    return max_dd


# 计算资金曲线
def equity_curve_with_long_and_short(df, leverage_rate=1, c_rate=3.0 / 1000, min_margin_rate=0.15):
    """
    :param df:  带有signal和pos的原始数据
    :param leverage_rate:  bfx交易所最多提供3倍杠杆，leverage_rate可以在(0, 3]区间选择
    :param c_rate:  手续费
    :param min_margin_rate:  低保证金比例，必须占到借来资产的15%
    :return:
    """

    # =====基本参数
    init_cash = 100  # 初始资金
    min_margin = init_cash * leverage_rate * min_margin_rate  # 最低保证金

    # =====根据pos计算资金曲线
    # ===计算涨跌幅
    df['change'] = df['close'].pct_change(1)  # 根据收盘价计算涨跌幅
    df['buy_at_open_change'] = df['close'] / df['open'] - 1  # 从今天开盘买入，到今天收盘的涨跌幅
    df['sell_next_open_change'] = df['open'].shift(-1) / df['close'] - 1  # 从今天收盘到明天开盘的涨跌幅
    df.at[len(df) - 1, 'sell_next_open_change'] = 0

    # ===选取开仓、平仓条件
    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(1)
    open_pos_condition = condition1 & condition2

    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(-1)
    close_pos_condition = condition1 & condition2

    # ===对每次交易进行分组
    df.loc[open_pos_condition, 'start_time'] = df['candle_begin_time']
    df['start_time'].fillna(method='ffill', inplace=True)
    df.loc[df['pos'] == 0, 'start_time'] = pd.NaT

    # ===计算仓位变动
    # 开仓时仓位, 建仓后的仓位
    df.loc[open_pos_condition, 'position'] = init_cash * leverage_rate * (1 + df['buy_at_open_change'])

    # 开仓后每天的仓位的变动
    group_num = len(df.groupby('start_time'))

    if group_num > 1:
        t = df.groupby('start_time').apply(
            lambda x: x['close'] / x.iloc[0]['close'] * x.iloc[0]['position']
        )
        t = t.reset_index(level=[0])
        df['position'] = t['close']
    elif group_num == 1:
        t = df.groupby('start_time')[['close', 'position']].apply(
            lambda x: x['close'] / x.iloc[0]['close'] * x.iloc[0]['position'])
        df['position'] = t.T.iloc[:, 0]

    # 每根K线仓位的最大值和最小值，针对最高价和最低价
    df['position_max'] = df['position'] * df['high'] / df['close']
    df['position_min'] = df['position'] * df['low'] / df['close']

    # 平仓时仓位
    df.loc[close_pos_condition, 'position'] *= (1 + df.loc[close_pos_condition, 'sell_next_open_change'])

    # ===计算每天实际持有资金的变化
    # 计算持仓利润
    df['profit'] = (df['position'] - init_cash * leverage_rate) * df['pos']  # 持仓盈利或者损失

    # 计算持仓利润最小值
    df.loc[df['pos'] == 1, 'profit_min'] = (df['position_min'] - init_cash * leverage_rate) * df[
        'pos']  # 最小持仓盈利或者损失
    df.loc[df['pos'] == -1, 'profit_min'] = (df['position_max'] - init_cash * leverage_rate) * df[
        'pos']  # 最小持仓盈利或者损失

    # 计算实际资金量
    df['cash'] = init_cash + df['profit']  # 实际资金
    df['cash'] -= init_cash * leverage_rate * c_rate  # 减去建仓时的手续费
    df['cash_min'] = df['cash'] - (df['profit'] - df['profit_min'])  # 实际最小资金
    df.loc[df['cash_min'] < 0, 'cash_min'] = 0  # 如果有小于0，直接设置为0
    df.loc[close_pos_condition, 'cash'] -= df.loc[close_pos_condition, 'position'] * c_rate  # 减去平仓时的手续费

    # ===判断是否会爆仓
    _index = df[df['cash_min'] <= min_margin].index

    if len(_index) > 0:
        print('有爆仓')

        df.loc[_index, '强平'] = 1
        df['强平'] = df.groupby('start_time')['强平'].fillna(method='ffill')
        df.loc[(df['强平'] == 1) & (df['强平'].shift(1) != 1), 'cash_强平'] = df['cash_min']  # 此处是有问题的
        df.loc[(df['pos'] != 0) & (df['强平'] == 1), 'cash'] = None
        df['cash'].fillna(value=df['cash_强平'], inplace=True)
        df['cash'] = df.groupby('start_time')['cash'].fillna(method='ffill')
        df.drop(['强平', 'cash_强平'], axis=1, inplace=True)  # 删除不必要的数据

    # ===计算资金曲线
    df['equity_change'] = df['cash'].pct_change()
    df.loc[open_pos_condition, 'equity_change'] = df.loc[open_pos_condition, 'cash'] / init_cash - 1  # 开仓日的收益率
    df['equity_change'].fillna(value=0, inplace=True)
    df['equity_curve'] = (1 + df['equity_change']).cumprod()

    # ===判断资金曲线是否有负值，有的话后面都置成0
    if len(df[df['equity_curve'] < 0]) > 0:
        neg_start = df[df['equity_curve'] < 0].index[0]
        df.loc[neg_start:, 'equity_curve'] = 0

    # ===删除不必要的数据
    df.drop(['change', 'buy_at_open_change', 'sell_next_open_change', 'position', 'position_max',
             'position_min', 'profit', 'profit_min', 'cash', 'cash_min'], axis=1, inplace=True)

    return df


# 输入价格数据,参数，输出收益率，最大回撤
def cal_rtn_sr(df1, para):
    df = df1.copy()
    freq_list = ['15T', '30T', '1H']
    df = df.resample(rule=freq_list[int(para[-1])], on='candle_begin_time', base=0,
                     label='left',
                     closed='left').agg(
        {'open': 'first',
         'high': 'max',
         'low': 'min',
         'close': 'last',
         'volume': 'sum',
         }
    )
    df.reset_index(inplace=True)
    df_s, trade_count = signal_bolling_with_stop_lose(df, para=para)
    df_res = equity_curve_with_long_and_short(df_s)
    df_res.sort_values(by='candle_begin_time', inplace=True)
    df_res.reset_index(inplace=True, drop=True)
    start_date = df_res.at[0, 'candle_begin_time']
    end_date = df_res.at[len(df_res) - 1, 'candle_begin_time']
    period = (end_date - start_date).days
    # cal year yield
    yyield = (df_res.at[len(df_res) - 1, 'equity_curve'] - 1) * 365 / period
    # cal sr ratio
    df_res = df_res[['candle_begin_time', 'equity_curve']]
    df_res = df_res.resample(rule='1D', on='candle_begin_time', base=0,
                             label='left',
                             closed='left').agg(
        {'equity_curve': 'first',
         }
    )
    df_res['rtn'] = df_res['equity_curve'] / df_res['equity_curve'].shift(1) - 1
    if df_res['rtn'].mean() != 0:
        mdd = my_cal_mdd(df_res, 'equity_curve')
    else:
        yyield = 0
        mdd = 1e-5
    return yyield, mdd


# 目标函数，返还种群观测值矩阵
def subAimFunc(args):
    i = args[0]
    Vars = args[1]
    data = args[2]
    period = Vars[i, 0] * 20
    s = Vars[i, 1] / 2
    stop_loss = Vars[i, 2]
    freq = Vars[i, 3]
    res = cal_rtn_sr(data, para=[period, s, stop_loss, freq])
    ObjV_i = list(res)
    return ObjV_i


# --------- 目标函数定义完毕

# 定义优化问题
class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self, PoolType, data):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 2  # 初始化M（目标维数）
        maxormins = [-1, 1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 4  # 初始化Dim（决策变量维数）#p1：期数.p2:轨道宽度，p3：止损,p4,周期，0：15T，1：30T，2：1H
        varTypes = [1, 1, 1, 1]  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [3, 2, 2, 0]  # 决策变量下界
        ub = [15, 10, 10, 2]  # 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)
        # 目标函数计算中用到的一些数据

        self.data = data
        self.gen_counts = 0

        # 设置用多线程还是多进程
        self.PoolType = PoolType
        if self.PoolType == 'Thread':
            self.pool = ThreadPool(8)  # 设置池的大小
        elif self.PoolType == 'Process':
            num_cores = int(mp.cpu_count())  # 获得计算机的核心数
            self.pool = ProcessPool(num_cores)  # 设置池的大小

    def aimFunc(self, pop):  # 目标函数
        self.gen_counts += 1
        Vars = pop.Phen  # 得到决策变量矩阵
        args = list(
            zip(
                list(range(pop.sizes)), [Vars] * pop.sizes, [self.data] * pop.sizes
            )
        )
        if self.PoolType == 'Thread':
            pop.ObjV = np.array(list(self.pool.map(subAimFunc, args)))
        elif self.PoolType == 'Process':
            result = self.pool.map_async(subAimFunc, args)
            result.wait()
            res = np.array(result.get())
            pop.ObjV = res

    # 重写进化终止条件


class moea_NSGA3_templet_auto_terminate(ea.moea_NSGA3_templet):
    def __init__(self, problem, population):
        ea.moea_NSGA3_templet.__init__(self, problem, population)
        self.pop_mean_aim1 = []
        self.pop_mean_aim2 = []

    def terminated(self, population):
        """
        描述:
            该函数用于判断是否应该终止进化，population为传入的种群
            重写终止进化方法，得到最优目标值
        """
        self.stat(population)  # 分析记录当代种群的数据
        # 判断是否终止进化，由于代数是从0数起，因此在比较currentGen和MAXGEN时需要对currentGen加1
        self.pop_mean_aim1.append(population.ObjV[:, 0].mean())
        self.pop_mean_aim2.append(population.ObjV[:, 1].mean())
        self.condition0 = False
        if len(self.pop_mean_aim2) > 3:
            try:
                diff1 = 1 - np.mean(self.pop_mean_aim1[-3:]) / self.pop_mean_aim1[-1]
                diff2 = 1 - np.mean(self.pop_mean_aim2[-3:]) / self.pop_mean_aim2[-1]
                print('种群进化率：', self.pop_mean_aim1[-1], diff1, self.pop_mean_aim2[-1], diff2)
                if abs(diff1) < 0.02 and abs(diff2) < 0.02:
                    print('种群已稳定，终止进化')
                    self.condition0 = True
            except Exception as e:
                print(e)
                pass

        if self.currentGen + 1 >= self.MAXGEN or self.condition0:
            print("结束迭代")
            return True
        else:
            self.currentGen += 1  # 进化代数+1
            return False


# 开始进化之旅
if __name__ == '__main__':
    data = pd.read_csv(r'D:\Work\cta_v2\GA\BTCUSD.csv')
    problem = MyProblem('Process', data)
    Encoding = 'BG'  # 编码方式
    NIND = nide  # 种群规模
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)
    population = ea.Population(Encoding, Field, NIND)
    myAlgorithm = moea_NSGA3_templet_auto_terminate(problem, population)
    myAlgorithm.MAXGEN = max_gen  # 最大进化代数
    myAlgorithm.drawing = 0  # 禁止绘图
    NDSet = myAlgorithm.run()  # 执行算法模板，得到帕累托最优解集NDSet
    para_Phen = NDSet.Phen  # 表现型
    para_ObjV = NDSet.ObjV  # 目标观测值
    print('用时：%s 秒' % (myAlgorithm.passTime))
    res_array = np.hstack((para_Phen, para_ObjV))
    df = pd.DataFrame(res_array)
    df.to_csv('temp.csv')  # 保存最终种群
    problem.pool.close()  # 关闭进程
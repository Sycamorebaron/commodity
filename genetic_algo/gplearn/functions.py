"""The functions used to create programs.

The :mod:`gplearn.functions` module contains all of the functions used by
gplearn programs. It also contains helper methods for a user to define their
own custom functions.
"""

# Author: Trevor Stephens <trevorstephens.com>
#
# License: BSD 3 clause

import numpy as np
import pandas as pd
from joblib import wrap_non_picklable_objects

__all__ = ['make_function']


class _Function(object):

    """A representation of a mathematical relationship, a node in a program.

    This object is able to be called with NumPy vectorized arguments and return
    a resulting vector based on a mathematical relationship.

    Parameters
    ----------
    function : callable
        A function with signature function(x1, *args) that returns a Numpy
        array of the same shape as its arguments.

    name : str
        The name for the function as it should be represented in the program
        and its visualizations.

    arity : int
        The number of arguments that the ``function`` takes.

    """

    def __init__(self, function, name, arity):
        self.function = function
        self.name = name
        self.arity = arity

    def __call__(self, *args):
        return self.function(*args)


def make_function(function, name, arity, wrap=True):
    """Make a function node, a representation of a mathematical relationship.

    This factory function creates a function node, one of the core nodes in any
    program. The resulting object is able to be called with NumPy vectorized
    arguments and return a resulting vector based on a mathematical
    relationship.

    Parameters
    ----------
    function : callable
        A function with signature `function(x1, *args)` that returns a Numpy
        array of the same shape as its arguments.

    name : str
        The name for the function as it should be represented in the program
        and its visualizations.

    arity : int
        The number of arguments that the `function` takes.

    wrap : bool, optional (default=True)
        When running in parallel, pickling of custom functions is not supported
        by Python's default pickler. This option will wrap the function using
        cloudpickle allowing you to pickle your solution, but the evolution may
        run slightly more slowly. If you are running single-threaded in an
        interactive Python session or have no need to save the model, set to
        `False` for faster runs.

    """
    if not isinstance(arity, int):
        raise ValueError('arity must be an int, got %s' % type(arity))
    if not isinstance(function, np.ufunc):
        if function.__code__.co_argcount != arity:
            raise ValueError('arity %d does not match required number of '
                             'function arguments of %d.'
                             % (arity, function.__code__.co_argcount))
    if not isinstance(name, str):
        raise ValueError('name must be a string, got %s' % type(name))
    if not isinstance(wrap, bool):
        raise ValueError('wrap must be an bool, got %s' % type(wrap))

    # Check output shape
    args = [np.ones(10) for _ in range(arity)]
    try:
        function(*args)
    except ValueError:
        raise ValueError('supplied function %s does not support arity of %d.'
                         % (name, arity))
    if not hasattr(function(*args), 'shape'):
        raise ValueError('supplied function %s does not return a numpy array.'
                         % name)
    if function(*args).shape != (10,):
        raise ValueError('supplied function %s does not return same shape as '
                         'input vectors.' % name)

    # Check closure for zero & negative input arguments
    args = [np.zeros(10) for _ in range(arity)]
    if not np.all(np.isfinite(function(*args))):
        raise ValueError('supplied function %s does not have closure against '
                         'zeros in argument vectors.' % name)
    args = [-1 * np.ones(10) for _ in range(arity)]
    if not np.all(np.isfinite(function(*args))):
        raise ValueError('supplied function %s does not have closure against '
                         'negatives in argument vectors.' % name)

    if wrap:
        return _Function(function=wrap_non_picklable_objects(function),
                         name=name,
                         arity=arity)
    return _Function(function=function,
                     name=name,
                     arity=arity)


def _protected_division(x1, x2):
    """Closure of division (x1/x2) for zero denominator."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(np.abs(x2) > 0.001, np.divide(x1, x2), 1.)


def _protected_sqrt(x1):
    """Closure of square root for negative arguments."""
    return np.sqrt(np.abs(x1))


def _protected_log(x1):
    """Closure of log for zero arguments."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(np.abs(x1) > 0.001, np.log(np.abs(x1)), 0.)


def _protected_inverse(x1):
    """Closure of log for zero arguments."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(np.abs(x1) > 0.001, 1. / x1, 0.)


def _sigmoid(x1):
    """Special case of logistic function to transform to probabilities."""
    with np.errstate(over='ignore', under='ignore'):
        return 1 / (1 + np.exp(-x1))


add2 = _Function(function=np.add, name='add', arity=2)
sub2 = _Function(function=np.subtract, name='sub', arity=2)
mul2 = _Function(function=np.multiply, name='mul', arity=2)
div2 = _Function(function=_protected_division, name='div', arity=2)
sqrt1 = _Function(function=_protected_sqrt, name='sqrt', arity=1)
log1 = _Function(function=_protected_log, name='log', arity=1)
neg1 = _Function(function=np.negative, name='neg', arity=1)
inv1 = _Function(function=_protected_inverse, name='inv', arity=1)
abs1 = _Function(function=np.abs, name='abs', arity=1)
max2 = _Function(function=np.maximum, name='max', arity=2)
min2 = _Function(function=np.minimum, name='min', arity=2)
sin1 = _Function(function=np.sin, name='sin', arity=1)
cos1 = _Function(function=np.cos, name='cos', arity=1)
tan1 = _Function(function=np.tan, name='tan', arity=1)
sig1 = _Function(function=_sigmoid, name='sig', arity=1)

# ----------------------------- 自定义函数 ------------------------------------
def __sign(x):
    return x / x.abs()

def __rank(x):
    """第i个元素在X中的分位数"""
    x = pd.Series(x)
    return pd.Series([len(x.loc[x < i]) / len(x) for i in x])

def __delay_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.shift(d))

def __delay_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.shift(d))

def __delay_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.shift(d))

def __delay_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.shift(d))

def __ts_corr_5(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 5
    return pd.Series(x.rolling(d).corr(y))

def __ts_corr_10(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 10
    return pd.Series(x.rolling(d).corr(y))

def __ts_corr_15(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 15
    return pd.Series(x.rolling(d).corr(y))

def __ts_corr_20(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 20
    return pd.Series(x.rolling(d).corr(y))

def __ts_cov_5(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 5
    return pd.Series(x.rolling(d).cov(y))

def __ts_cov_10(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 10
    return pd.Series(x.rolling(d).cov(y))

def __ts_cov_15(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 15
    return pd.Series(x.rolling(d).cov(y))

def __ts_cov_20(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    d = 20
    return pd.Series(x.rolling(d).cov(y))

def __scale_1(x):
    x = pd.Series(x)
    a = 1
    return pd.Series(x.apply(lambda i: i * a / sum(abs(x))))

def __scale_2(x):
    x = pd.Series(x)
    a = 2
    return pd.Series(x.apply(lambda i: i * a / sum(abs(x))))

def __scale_3(x):
    x = pd.Series(x)
    a = 3
    return pd.Series(x.apply(lambda i: i * a / sum(abs(x))))

def __scale_4(x):
    x = pd.Series(x)
    a = 1
    return pd.Series(x.apply(lambda i: i * a / sum(abs(x))))

def __delta_1(x):
    x = pd.Series(x)
    return pd.Series(x - x.shift(1))

def __delta_2(x):
    x = pd.Series(x)
    return pd.Series(x - x.shift(2))

def __delta_3(x):
    x = pd.Series(x)
    return pd.Series(x - x.shift(3))

def __delta_4(x):
    x = pd.Series(x)
    return pd.Series(x - x.shift(4))

def __signedpower_2(x):
    x = pd.Series(x)
    a = 2
    return pd.Series(pd.Series(__sign(x)) * x.apply(lambda i: i**a))

def __signedpower_3(x):
    x = pd.Series(x)
    a = 3
    return pd.Series(pd.Series(__sign(x)) * x.apply(lambda i: i**a))

def __signedpower_4(x):
    x = pd.Series(x)
    a = 4
    return pd.Series(pd.Series(__sign(x)) * x.apply(lambda i: i**a))

def __signedpower_5(x):
    x = pd.Series(x)
    a = 5
    return pd.Series(pd.Series(__sign(x)) * x.apply(lambda i: i**a))

def __decay_linear_5(x):
    x = pd.Series(x)
    d = 5
    vector_d = [(i + 1) / ((1 + d) * d) * 2 for i in range(d)]
    return pd.Series(x.rolling(d).apply(lambda j: np.dot(j, vector_d)))

def __decay_linear_10(x):
    x = pd.Series(x)
    d = 10
    vector_d = [(i + 1) / ((1 + d) * d) * 2 for i in range(d)]
    return pd.Series(x.rolling(d).apply(lambda j: np.dot(j, vector_d)))

def __decay_linear_15(x):
    x = pd.Series(x)
    d = 15
    vector_d = [(i + 1) / ((1 + d) * d) * 2 for i in range(d)]
    return pd.Series(x.rolling(d).apply(lambda j: np.dot(j, vector_d)))

def __decay_linear_20(x):
    x = pd.Series(x)
    d = 20
    vector_d = [(i + 1) / ((1 + d) * d) * 2 for i in range(d)]
    return pd.Series(x.rolling(d).apply(lambda j: np.dot(j, vector_d)))


def __ts_min_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).min())

def __ts_min_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).min())

def __ts_min_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).min())

def __ts_min_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).min())

def __ts_max_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).max())

def __ts_max_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).max())

def __ts_max_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).max())

def __ts_max_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).max())

def __ts_argmin_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).apply(lambda i: i.argmin()))

def __ts_argmin_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).apply(lambda i: i.argmin()))

def __ts_argmin_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).apply(lambda i: i.argmin()))

def __ts_argmin_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).apply(lambda i: i.argmin()))

def __ts_argmax_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).apply(lambda i: i.argmax()))

def __ts_argmax_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).apply(lambda i: i.argmax()))

def __ts_argmax_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).apply(lambda i: i.argmax()))

def __ts_argmax_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).apply(lambda i: i.argmax()))

def __ts_rank_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).apply(lambda x: len(x.loc[x < x.iloc[-1]]) / len(x)))

def __ts_rank_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).apply(lambda x: len(x.loc[x < x.iloc[-1]]) / len(x)))

def __ts_rank_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).apply(lambda x: len(x.loc[x < x.iloc[-1]]) / len(x)))

def __ts_rank_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).apply(lambda x: len(x.loc[x < x.iloc[-1]]) / len(x)))

def __ts_sum_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).sum())

def __ts_sum_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).sum())

def __ts_sum_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).sum())

def __ts_sum_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).sum())

def __ts_prod_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).apply(lambda i: np.prod(i)))

def __ts_prod_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).apply(lambda i: np.prod(i)))

def __ts_prod_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).apply(lambda i: np.prod(i)))

def __ts_prod_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).apply(lambda i: np.prod(i)))

def __ts_stddev_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).std(ddof=1))

def __ts_stddev_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).std(ddof=1))

def __ts_stddev_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).std(ddof=1))

def __ts_stddev_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).std(ddof=1))

def __ts_zscore_5(x):
    x = pd.Series(x)
    d = 5
    return pd.Series(x.rolling(d).mean() / x.rolling(d).std(ddof=1))

def __ts_zscore_10(x):
    x = pd.Series(x)
    d = 10
    return pd.Series(x.rolling(d).mean() / x.rolling(d).std(ddof=1))

def __ts_zscore_15(x):
    x = pd.Series(x)
    d = 15
    return pd.Series(x.rolling(d).mean() / x.rolling(d).std(ddof=1))

def __ts_zscore_20(x):
    x = pd.Series(x)
    d = 20
    return pd.Series(x.rolling(d).mean() / x.rolling(d).std(ddof=1))

def __rank_sub(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    return pd.Series(pd.Series(__rank(x)) - pd.Series(__rank(y)))

def __rank_div(x, y):
    x = pd.Series(x)
    y = pd.Series(y)
    return pd.Series(pd.Series(__rank(x)) / pd.Series(__rank(y)))

def __sigmoid(x):
    x = pd.Series(x)
    return pd.Series(x.apply(lambda i: 1 / (1 + np.exp(-i))))

rank = _Function(function=__rank, name='rank', arity=1)
delay_5 = _Function(function=__delay_5, name='delay_5', arity=1)
delay_10 = _Function(function=__delay_10, name='delay_10', arity=1)
delay_15 = _Function(function=__delay_15, name='delay_15', arity=1)
delay_20 = _Function(function=__delay_20, name='delay_20', arity=1)
ts_corr_5 = _Function(function=__ts_corr_5, name='ts_corr_5', arity=2)
ts_corr_10 = _Function(function=__ts_corr_10, name='ts_corr_10', arity=2)
ts_corr_15 = _Function(function=__ts_corr_15, name='ts_corr_15', arity=2)
ts_corr_20 = _Function(function=__ts_corr_20, name='ts_corr_20', arity=2)
ts_cov_5 = _Function(function=__ts_cov_5, name='ts_cov_5', arity=2)
ts_cov_10 = _Function(function=__ts_cov_10, name='ts_cov_10', arity=2)
ts_cov_15 = _Function(function=__ts_cov_15, name='ts_cov_15', arity=2)
ts_cov_20 = _Function(function=__ts_cov_20, name='ts_cov_20', arity=2)
scale_1 = _Function(function=__scale_1, name='scale_1', arity=1)
scale_2 = _Function(function=__scale_2, name='scale_2', arity=1)
scale_3 = _Function(function=__scale_3, name='scale_3', arity=1)
scale_4 = _Function(function=__scale_4, name='scale_4', arity=1)
delta_1 = _Function(function=__delta_1, name='delta_1', arity=1)
delta_2 = _Function(function=__delta_2, name='delta_2', arity=1)
delta_3 = _Function(function=__delta_3, name='delta_3', arity=1)
delta_4 = _Function(function=__delta_4, name='delta_4', arity=1)
signedpower_2 = _Function(function=__signedpower_2, name='signedpower_2', arity=1)
signedpower_3 = _Function(function=__signedpower_3, name='signedpower_3', arity=1)
signedpower_4 = _Function(function=__signedpower_4, name='signedpower_4', arity=1)
signedpower_5 = _Function(function=__signedpower_5, name='signedpower_5', arity=1)
decay_linear_5 = _Function(function=__decay_linear_5, name='decay_linear_5', arity=1)
decay_linear_10 = _Function(function=__decay_linear_10, name='decay_linear_10', arity=1)
decay_linear_15 = _Function(function=__decay_linear_15, name='decay_linear_15', arity=1)
decay_linear_20 = _Function(function=__decay_linear_20, name='decay_linear_20', arity=1)
ts_min_5 = _Function(function=__ts_min_5, name='ts_min_5', arity=1)
ts_min_10 = _Function(function=__ts_min_10, name='ts_min_10', arity=1)
ts_min_15 = _Function(function=__ts_min_15, name='ts_min_15', arity=1)
ts_min_20 = _Function(function=__ts_min_20, name='ts_min_20', arity=1)
ts_max_5 = _Function(function=__ts_max_5, name='ts_max_5', arity=1)
ts_max_10 = _Function(function=__ts_max_10, name='ts_max_10', arity=1)
ts_max_15 = _Function(function=__ts_max_15, name='ts_max_15', arity=1)
ts_max_20 = _Function(function=__ts_max_20, name='ts_max_20', arity=1)
ts_argmin_5 = _Function(function=__ts_argmin_5, name='ts_argmin_5', arity=1)
ts_argmin_10 = _Function(function=__ts_argmin_10, name='ts_argmin_10', arity=1)
ts_argmin_15 = _Function(function=__ts_argmin_15, name='ts_argmin_15', arity=1)
ts_argmin_20 = _Function(function=__ts_argmin_20, name='ts_argmin_20', arity=1)
ts_argmax_5 = _Function(function=__ts_argmax_5, name='ts_argmax_5', arity=1)
ts_argmax_10 = _Function(function=__ts_argmax_10, name='ts_argmax_10', arity=1)
ts_argmax_15 = _Function(function=__ts_argmax_15, name='ts_argmax_15', arity=1)
ts_argmax_20 = _Function(function=__ts_argmax_20, name='ts_argmax_20', arity=1)
ts_rank_5 = _Function(function=__ts_rank_5, name='ts_rank_5', arity=1)
ts_rank_10 = _Function(function=__ts_rank_10, name='ts_rank_10', arity=1)
ts_rank_15 = _Function(function=__ts_rank_15, name='ts_rank_15', arity=1)
ts_rank_20 = _Function(function=__ts_rank_20, name='ts_rank_20', arity=1)
ts_sum_5 = _Function(function=__ts_sum_5, name='ts_sum_5', arity=1)
ts_sum_10 = _Function(function=__ts_sum_10, name='ts_sum_10', arity=1)
ts_sum_15 = _Function(function=__ts_sum_15, name='ts_sum_15', arity=1)
ts_sum_20 = _Function(function=__ts_sum_20, name='ts_sum_20', arity=1)
ts_prod_5 = _Function(function=__ts_prod_5, name='ts_prod_5', arity=1)
ts_prod_10 = _Function(function=__ts_prod_10, name='ts_prod_10', arity=1)
ts_prod_15 = _Function(function=__ts_prod_15, name='ts_prod_15', arity=1)
ts_prod_20 = _Function(function=__ts_prod_20, name='ts_prod_20', arity=1)
ts_stddev_5 = _Function(function=__ts_stddev_5, name='ts_stddev_5', arity=1)
ts_stddev_10 = _Function(function=__ts_stddev_10, name='ts_stddev_10', arity=1)
ts_stddev_15 = _Function(function=__ts_stddev_15, name='ts_stddev_15', arity=1)
ts_stddev_20 = _Function(function=__ts_stddev_20, name='ts_stddev_20', arity=1)
ts_zscore_5 = _Function(function=__ts_zscore_5, name='ts_zscore_5', arity=1)
ts_zscore_10 = _Function(function=__ts_zscore_10, name='ts_zscore_10', arity=1)
ts_zscore_15 = _Function(function=__ts_zscore_15, name='ts_zscore_15', arity=1)
ts_zscore_20 = _Function(function=__ts_zscore_20, name='ts_zscore_20', arity=1)
rank_sub = _Function(function=__rank_sub, name='rank_sub', arity=2)
rank_div = _Function(function=__rank_div, name='rank_div', arity=2)
sigmoid = _Function(function=__sigmoid, name='sigmoid', arity=1)

# ----------------------------- 自定义函数 ------------------------------------

_function_map = {
    'add': add2,
    'sub': sub2,
    'mul': mul2,
    'div': div2,
    'sqrt': sqrt1,
    'log': log1,
    'abs': abs1,
    'neg': neg1,
    'inv': inv1,
    'max': max2,
    'min': min2,
    'sin': sin1,
    'cos': cos1,
    'tan': tan1,

    'rank': rank,
    'delay_5': delay_5,
    'delay_10': delay_5,
    'delay_15': delay_15,
    'delay_20': delay_20,
    'ts_corr_5': ts_corr_5,
    'ts_corr_10': ts_corr_10,
    'ts_corr_15': ts_corr_15,
    'ts_corr_20': ts_corr_20,
    'ts_cov_5': ts_cov_5,
    'ts_cov_10': ts_cov_10,
    'ts_cov_15': ts_cov_15,
    'ts_cov_20': ts_cov_20,
    'scale_1': scale_1,
    'scale_2': scale_2,
    'scale_3': scale_3,
    'scale_4': scale_4,
    'delta_1': delta_1,
    'delta_2': delta_2,
    'delta_3': delta_3,
    'delta_4': delta_4,
    'signedpower_2': signedpower_2,
    'signedpower_3': signedpower_3,
    'signedpower_4': signedpower_4,
    'signedpower_5': signedpower_5,
    'decay_linear_5': decay_linear_5,
    'decay_linear_10': decay_linear_10,
    'decay_linear_15': decay_linear_15,
    'decay_linear_20': decay_linear_20,
    'ts_min_5': ts_min_5,
    'ts_min_10': ts_min_10,
    'ts_min_15': ts_min_15,
    'ts_min_20': ts_min_20,
    'ts_max_5': ts_max_5,
    'ts_max_10': ts_max_10,
    'ts_max_15': ts_max_15,
    'ts_max_20': ts_max_20,
    'ts_argmin_5': ts_argmin_5,
    'ts_argmin_10': ts_argmin_10,
    'ts_argmin_15': ts_argmin_15,
    'ts_argmin_20': ts_argmin_20,
    'ts_argmax_5': ts_argmax_5,
    'ts_argmax_10': ts_argmax_10,
    'ts_argmax_15': ts_argmax_15,
    'ts_argmax_20': ts_argmax_20,
    'ts_rank_5': ts_rank_5,
    'ts_rank_10': ts_rank_10,
    'ts_rank_15': ts_rank_15,
    'ts_rank_20': ts_rank_20,
    'ts_sum_5': ts_sum_5,
    'ts_sum_10': ts_sum_10,
    'ts_sum_15': ts_sum_15,
    'ts_sum_20': ts_sum_20,
    'ts_prod_5': ts_prod_5,
    'ts_prod_10': ts_prod_10,
    'ts_prod_15': ts_prod_15,
    'ts_prod_20': ts_prod_20,
    'ts_stddev_5': ts_stddev_5,
    'ts_stddev_10': ts_stddev_10,
    'ts_stddev_15': ts_stddev_15,
    'ts_stddev_20': ts_stddev_20,
    'ts_zscore_5': ts_zscore_5,
    'ts_zscore_10': ts_zscore_10,
    'ts_zscore_15': ts_zscore_15,
    'ts_zscore_20': ts_zscore_20,
    'rank_sub': rank_sub,
    'rank_div': rank_div,
    'sigmoid': sigmoid,
}


if __name__ == '__main__':
    print(_function_map.keys())
    exit()
    test_data = pd.read_csv(r'D:\commodity\data\1d_exp_ic.csv')
    x = test_data['1dvol_oi']
    y = test_data['1dstd'].abs()

    # print(y)
    x = np.array(x)
    print(type(x))
    print(x)

    res = scale_2(x, y)

    print(type(res))
    print(res)
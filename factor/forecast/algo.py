import pandas as pd
import statsmodels.api as sm
import sklearn.tree as st

pd.set_option('expand_frame_repr', False)


class Algo:

    def ols(self, x, y, **kwargs):
        model = sm.OLS(endog=y, exog=x)
        res = model.fit()
        return res.fittedvalues

    def decision_tree(self, x, y, **kwargs):
        """
        决策树，
        :param x:
        :param y:
        :param kwargs: max_depth
        :return:
        """
        model = st.DecisionTreeRegressor(max_depth=kwargs['max_depth'])
        model.fit(X=x, y=y)
        pred_y = model.predict(X=x)

        return pd.DataFrame(pred_y)

    def xgb(self, x, y, **kwargs):
        pass

    def logit(self, x, y, **kwargs):
        pass


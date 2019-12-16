
# 1. 实现多因子 买卖;
# 2. 实现评估
# 3. 讲多因子组合策略实践
# 4. 理论上，可以实现多周期 5分钟 15分钟 30 60 等各种策略，进行统一比较
# 5. AbuPickTimeWorker 派生或者agent 管理 KL数据由上层传入?
# 6. 多股票数据？ 组合评估？
# 7. 派生 : AbuOrder,回测没有关系？
import seaborn as sns
import numpy as np
import pandas as pd
from QAStrategy.qastockbase import QAStrategyStockBase
from abupy import AbuPickTimeWorker, AbuFactorBuyBreak, AbuFactorSellBreak, AbuFactorPreAtrNStop, \
    AbuFactorCloseAtrNStop, AbuFactorAtrNStop, AbuBenchmark, AbuCapital


class QAStrategyPickTime(QAStrategyStockBase):

    #
    def __init__(self):
        from abupy import AbuSlippageBuyBase

        # 修改g_open_down_rate的值为0.02
        g_open_down_rate = 0.02

        # noinspection PyClassHasNoInit
        class AbuSlippageBuyMean2(AbuSlippageBuyBase):
            def fit_price(self):
                if (self.kl_pd_buy.open / self.kl_pd_buy.pre_close) < (
                        1 - g_open_down_rate):
                    # 开盘下跌K_OPEN_DOWN_RATE以上，单子失效
                    print(self.factor_name + 'open down threshold')
                    return np.inf
                # 买入价格为当天均价
                self.buy_price = np.mean(
                    [self.kl_pd_buy['high'], self.kl_pd_buy['low']])
                return self.buy_price

        # 只针对60使用AbuSlippageBuyMean2
        buy_factors = [{'slippage': AbuSlippageBuyMean2, 'xd': 60, 'class': AbuFactorBuyBreak},
                        {'xd': 42, 'class': AbuFactorBuyBreak}]

        # 可以定义一堆的卖出条件...
        sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
        sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
        sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
        sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}

        sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]

        benchmark = AbuBenchmark()
        capital = AbuCapital(1000000, benchmark)

        self.pick_timer_worker = AbuPickTimeWorker(capital, self._market_data, benchmark, buy_factors, sell_factors)
        pass

    # 由模拟、实盘msg触发:
    def on_bar(self, data):
        print(data)
        print(self.get_positions('000001'))
        print(self.market_data)

        code = data.name[1]
        print('---------------under is 当前全市场的market_data --------------')

        print(self.get_current_marketdata())
        print('---------------under is 当前品种的market_data --------------')
        print(self.get_code_marketdata(code))
        print(code)
        self.pick_timer_worker._task_loop(data)
        # print(self.running_time)
        # input()


if __name__ == '__main__':
    # '000001',
    s = QAStrategyPickTime(code='000002', frequence='30min', start='2019-07-01', end='2019-07-05', strategy_id='x')
    s.run_sim()
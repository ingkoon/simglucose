from simglucose.simulation.scenario import Action, Scenario
import numpy as np
from scipy.stats import truncnorm
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 
class RandomScenario(Scenario):
    def __init__(self, start_time=None, seed=None):
        Scenario.__init__(self, start_time=start_time)
        self.seed = seed

    def get_action(self, t):
        # t must be datetime.datetime object
        delta_t = t - datetime.combine(t.date(), datetime.min.time())
        # 인자로 받은 시간을 초로 분해
        t_sec = delta_t.total_seconds()

        # 초 1초 이하일 경우 
        if t_sec < 1:
            #새로운 시나리오 작성
            logger.info('Creating new one day scenario ...')
            #create시나리오 실행
            self.scenario = self.create_scenario()

        # 초를 분단위로 변경
        t_min = np.floor(t_sec / 60.0)

        # scenario는 {'meal' : {'time': [], 'amount': []}}형태를 갖고 있음
        if t_min in self.scenario['meal']['time']:
            logger.info('Time for meal!')
            idx = self.scenario['meal']['time'].index(t_min)
            return Action(meal=self.scenario['meal']['amount'][idx])
        else:
            return Action(meal=0)

    #이거슨 식사량의 모평균과 모 표준편차의 표준편차를 구해서 시나리오의 식사량을,  신뢰구간의 상한과 하한을 바탕으로 랜덤값을 구하여 시나리오의 식사 시간을 구해주는 거시다 쉬불
    def create_scenario(self):
        scenario = {'meal': {'time': [],
                             'amount': []}}

        # Probability of taking each meal
        # [breakfast, snack1, lunch, snack2, dinner, snack3]
        # 각각 식사를 할 확률
        prob = [0.95, 0.3, 0.95, 0.3, 0.95, 0.3]
        #lb = 신뢰구간의 하한
        #ub = 신뢰구간의 상한
        #mu = 모평균
        #sigma = 모표준편차
        # 배열요소 6개는 각각의 식사량에 대한 인자.
        time_lb = np.array([5, 9, 10, 14, 16, 20]) * 60
        time_ub = np.array([9, 10, 14, 16, 20, 23]) * 60
        #lb와  uB의 모평균 값이 mu이다.
        time_mu = np.array([7, 9.5, 12, 15, 18, 21.5]) * 60
        time_sigma = np.array([60, 30, 60, 30, 60, 30])
        amount_mu = [45, 10, 70, 10, 80, 10]
        amount_sigma = [10, 5, 10, 5, 10, 5]

        for p, tlb, tub, tbar, tsd, mbar, msd in zip(
                prob, time_lb, time_ub, time_mu, time_sigma,
                amount_mu, amount_sigma):
            if self.random_gen.rand() < p:
                tmeal = np.round(truncnorm.rvs(a=(tlb - tbar) / tsd,
                                               b=(tub - tbar) / tsd,
                                               loc=tbar,
                                               scale=tsd,
                                               random_state=self.random_gen))
                scenario['meal']['time'].append(tmeal)
                scenario['meal']['amount'].append(
                    max(round(self.random_gen.normal(mbar, msd)), 0))

        return scenario

    def reset(self):
        self.random_gen = np.random.RandomState(self.seed)
        self.scenario = self.create_scenario()

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, seed):
        self._seed = seed
        self.reset()


if __name__ == '__main__':
    from datetime import time
    from datetime import timedelta
    import copy
    now = datetime.now()
    t0 = datetime.combine(now.date(), time(6, 0, 0, 0))
    t = copy.deepcopy(t0)
    sim_time = timedelta(days=2)

    scenario = RandomScenario(seed=1)
    m = []
    T = []
    while t < t0 + sim_time:
        action = scenario.get_action(t)
        m.append(action.meal)
        T.append(t)
        t += timedelta(minutes=1)

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    plt.plot(T, m)
    ax = plt.gca()
    ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M\n'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('\n%b %d'))
    plt.show()

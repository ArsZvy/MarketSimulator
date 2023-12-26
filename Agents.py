import pandas as pd
from random import random as r, sample

class good():

    def __init__(self, ID, depreciation):
        self.ID = ID # ID of a good
        self.depreciation = depreciation # depreciates goods over time

    def depreciate(self, quant):
        return self.depreciation(quant)


class goods_market():

    def __init__(self, goods, consumers, producers):
        self.name = 'goods' # name of a market: "goods", "labor", "real estate", "stock exchange" etc
        self.goods = goods
        self.consumers = consumers
        self.producers = producers
        self.spread = {} # stores sell offers: {good_ID: [(price, quantity, seller), ...]}
        self.trans_arch = {} # archieve of statistics of daily transactions: {time: {good_ID: (avg, std, min_price, max_price, items sold)}}
        self.trans_today = {} # transactions that happen today
        for good_ID in self.goods: # DO NOT TOUCH THIS, it is needed to correctly start the simulation (look start_simulation)
            self.trans_today[good_ID] = []
        self.census_ = None # census object is connected when census_ is initialized
    
    def __str__(self):
        return '-' * 10 + '\nGoods market print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10
    
    def fake_data(self): # generate fake data for day 0
        self.trans_arch[0] = {}
        for good_ID in self.goods:
            avg_price = 100 * r() + 10
            self.trans_today[good_ID] = [(5, avg_price)]

    def reset_day(self): # reset all the day-to-day variables
        self.spread = {}
        for name in self.goods:
            self.spread[name] = [[10**9, 0, None]] # list of sell offers, add the "barrier" offer that noone would ever take
            self.trans_today[name] = []

    def add_offer_sell(self, offers, seller): # add the offer to the spread
        if not seller.verify_good_seller(offers): # if not valid offer list -> do not add it
            return
        for good_ID, price, quant in offers:
            self.spread[good_ID].append([price, quant, seller])

    def sort_offers(self):
        for good_ID, cur_spread in self.spread.items():
            cur_spread.sort(key=lambda x: x[0])

    def find_offer(self, buyer): # tries to match buyer with some sell offer; return True if some transaction has happened
        done = False
        offers = buyer.request_good_offer()
        if not buyer.verify_good_buyer(offers):
            return False
        for good_ID, buy_price, buy_quant in buyer.request_good_offer():
            sell_price, sell_quant, seller = self.spread[good_ID][0]
            self.census_.file.write(' '.join(map(str, ['Deal under consideration (good_ID, sell_price, sell_quant, buy_price, buy_quant):', 
                                                       good_ID, sell_price, sell_quant, buy_price, buy_quant]))+'\n')
            if buy_price >= sell_price:
                self.census_.file.write('Deal accepted\n')
                done = True
                trans_quant = min(buy_quant, sell_quant)
                if trans_quant == sell_quant:
                    self.spread[good_ID].pop(0)
                else:
                    self.spread[good_ID][0][1] -= trans_quant
                seller.sell_good(good_ID, trans_quant, sell_price)
                buyer.purchase_good(good_ID, trans_quant, sell_price)
                self.trans_today[good_ID].append((trans_quant, sell_price))
                break
        return done

    def run_day(self): # here we actually run the day of trades
        self.census_.file.write('Started the day of trades (goods)!\n')
        all_IDs = [(key, 0) for key in self.consumers.keys()] + [(key, 1) for key in self.producers.keys()]
        all_set = set(sample(all_IDs, len(all_IDs)))
        while len(all_set) > 0:
            cur_ID, cur_type = all_set.pop()
            cur_buyer = self.consumers[cur_ID] if cur_type == 0 else self.producers[cur_ID]
            if self.find_offer(cur_buyer):
                all_set.add((cur_ID, cur_type))

    def calc_stat(self): # calculate (avg_price, std, min_price, max_price, items_sold) for each good_ID
        ans = {}
        for good_ID, trans_lst in self.trans_today.items():
            tot_sum, tot_num = 0, 0
            min_price, max_price = 10**9, -1
            for quant, price in trans_lst:
                tot_sum += quant * price
                tot_num += quant
                min_price = min(min_price, price)
                max_price = max(max_price, price)
            avg = tot_sum / tot_num if tot_num > 0 else -1
            tot_sqr = 0
            for quant, price in trans_lst:
                tot_sqr += quant * (price - avg)**2
            std = (tot_sqr / (tot_num - 1)) ** 0.5 if tot_num > 1 else -1
            if min_price == 10**9:
                min_price = -1
            if avg == -1:
                avg = self.trans_arch[self.census_.time-1][good_ID][0]
            ans[good_ID] = (avg, std, min_price, max_price, tot_num)
        self.trans_arch[self.census_.time] = ans
        
    def make_log(self): # logging process
        self.calc_stat()
        stat = self.trans_arch[self.census_.time]
        return [{
            'good ID': good_ID,
            'avg price': prices[0],
            'std price': prices[1],
            'min price': prices[2],
            'max price': prices[3],
            'items sold': prices[4],
            'time': self.census_.time
        } for good_ID, prices in stat.items()]


class labor_market():

    def __init__(self, consumers, producers):
        self.name = 'labor' # name of a market: "goods", "labor", "real estate", "stock exchange" etc
        self.consumers = consumers
        self.producers = producers
        self.census_ = None # census object is connected when census_ is initialized

    def reset_day(self):
        self.job_takers = set() # future employees
        self.job_givers = set() # future employers

    def add_taker(self, cons, salary):
        self.job_takers.add((cons.skill, salary, cons.ID))

    def add_giver(self, prod, skill, salary):
        self.job_givers.add((skill, salary, prod.ID))

    def run_day(self): # run the whole hiring cycle, FOR NOW EXTREMELY INEFFICIENT, IDK HOW TO IMPROVE IT LOL
        self.census_.file.write('Started the day of trades (labor)!\n')
        self.census_.file.write('Job takers (skill, salary, ID)\n')
        self.census_.file.write(str(self.job_takers))
        self.census_.file.write('Job givers\n')
        self.census_.file.write(str(self.job_givers))
        for job_taker in self.job_takers:
            for job_giver in self.job_givers:
                if job_taker[0] >= job_giver[0] and job_taker[1] <= job_giver[1]: # skillful enough and not too expensive -> hire
                    self.job_givers.remove(job_giver)
                    salary = job_taker[1]
                    employee = self.consumers[job_taker[2]]
                    employer = self.producers[job_giver[2]]
                    if employee.job is not None:
                        old_empl = employee.job[0]
                        old_empl.fire_employee(employee.ID)
                    self.census_.file.write(' '.join(map(str, ['Got a match (employer_ID, employee_ID, salary):', employer.ID, employee.ID, salary])) + '\n')
                    employer.hire_employee(employee, salary)
                    break


class consumer():
    
    def __init__(self, ID, util, cash, skill, goods):
        self.ID = ID # ID of a consumer
        self.goods = goods
        self.util = util # {good_ID : #} -> utils (a function that takes dict of goods utility)
        self.cash = cash # cash assets
        self.stored_goods = {}
        for name in self.goods:
            self.stored_goods[name] = 0
        self.skill = skill # skill (relevant for the job); later would make it a vector instead to represent different skills
        self.job = None # the job position of the type optional (employer, salary)
        self.spent_today = 0
        self.dividends = 0
        self.coins_for_util = 30 * (0.9 + 0.2*r()) # how much money are you willing to give for one util? Adjusted dynamically
        self.salary_expectation = 150 * (0.9 + 0.2*r()) # what is your expected salary?
        self.census_ = None # census object is connected when census_ is initialized
    
    def __str__(self):
        return '-' * 10 + '\nConsumer print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10

    def reset_day(self): # reset all the day-to-day variables
        self.spent_today = 0
        self.dividends = 0

    def depreciate_goods(self):
        for good_ID in self.stored_goods:
            self.stored_goods[good_ID] = self.goods[good_ID].depreciate(self.stored_goods[good_ID])

    def earn_salary(self):
        self.cash += self.job[1] if self.job is not None else 0
    
    def util_grad(self): # return {good_ID: change in utility if you increase the good by one}
        eps = 1.0
        ans = {}
        util_old = self.util(self.stored_goods)
        for good_ID in self.goods:
            new_pur_goods = self.stored_goods.copy()
            new_pur_goods[good_ID] += eps
            util_new = self.util(new_pur_goods)
            ans[good_ID] = (util_new - util_old) / eps
        return ans
    
    def calc_coins_for_util(self):
        # actual to ideal spending ratio
        ratio = self.spent_today / (max(self.dividends + self.job[1], self.cash / 10) if self.job is not None else self.cash / 10)
        # make it a bit more conservative (tends to the mean)
        ratio = ratio * 1/2 + 1/2
        # big ratio -> we should have smaller util value ()
        self.coins_for_util *= (0.95 + 0.1 * r()) / ratio

    def request_good_offer(self): # RETURN THE MAX PRICES FOR THE GOODS WE ARE READY TO PURCHASE: [(good_ID, price, quant), ...] (decreasing preferance)
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        grads = self.util_grad()
        ans = []
        for good_ID in grads:
            if grads[good_ID] > 0:
                price_bet = min(grads[good_ID] * self.coins_for_util, self.cash-30)
                if price_bet < 0:
                    continue
                ans.append((good_ID, price_bet, 1))
        return ans

    def verify_good_buyer(self, offers): # verify the offer (buyer side)
        return all([price*quant <= self.cash for good_ID, price, quant in offers])

    def purchase_good(self, good_ID, quant, price):
        self.cash -= quant * price
        self.stored_goods[good_ID] += quant
        self.spent_today += quant * price

    def request_job_offer(self): # RETURN THE DESIRED SALARY, 0 if not interested
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        if self.job is not None and r() > 0.2: # if already employed, do not search for a new job with 80% probability
            return 0
        return self.salary_expectation

    def calc_salary_expectation(self):
        market_salary = self.census_.stats['salary_skill_ratio'] * self.skill
        update_coef = market_salary / self.salary_expectation * 1/2 + 1/2 # a little more conservative
        if self.job is None: # unemployed -> reduce your expectations
            if update_coef < 1: # our expectation is indeed too high
                self.salary_expectation *= update_coef * (0.95 + 0.1 * r())
            else: # beggers are no choosers
                self.salary_expectation *= (0.85 + 0.1 * r())
        else: # employed -> raise your expectations
            if update_coef < 1: # you are lucky! You are earning more than the market
                self.salary_expectation *= (0.95 + 0.1 * r())
            else: # damn, you are good
                self.salary_expectation *= update_coef * (0.95 + 0.1 * r())

    def get_fired(self):
        self.job = None

    def get_hired(self, employer, salary): # details in the labor market
        self.job = (employer, salary) # tuple of employer (class producer) and salary
    
    def market_asset_evaluation(self):
        total = 0
        price_dict = self.census_.stats['goods_market_prices'][self.census_.time]
        for good_ID, num in self.stored_goods.items():
            price = max(price_dict[good_ID][0], 0)
            total += price * num
        return total

    def earn_dividends(self, payment):
        self.cash += payment
        self.dividends += payment
    
    def make_log(self): # logging
        return {
            'cons_ID': self.ID,
            'cash': self.cash,
            'no-cash assets value': self.market_asset_evaluation(),
            'salary': self.job[1] if self.job is not None else 0,
            'dividends': self.dividends,
            'spending': self.spent_today,
            'utility': self.util(self.stored_goods),
            'skill': self.skill,
            'time': self.census_.time
        }


class producer():

    def __init__(self, ID, start_cap, good_ID, fixed_cost, productivity, components, owner, stocks, goods):
        self.ID = ID # company ID
        self.good_ID = good_ID # the good ID the company is producing
        self.goods = goods
        self.fixed_cost = fixed_cost # the fixed cost; STUPID ASS IMIPLEMENTATION GOTTA CHANGE IT
        self.productivity = productivity # function that maps # of hours to the number of units produced
        self.stored_goods = {} # stored goods
        for good_ID in self.goods:
            self.stored_goods[good_ID] = 0
        self.cash = start_cap # the starting capital of the company
        self.components = components # {good_ID: #} -> number of each good needed to produce one unit of the desired good
        self.employees = {} # {consumer_ID: (consumer, salary)}
        self.stocks = stocks
        self.ownership = {owner.ID: (owner, stocks)}
        self.total_skill = 1
        self.revenue = 0
        self.units_sold = 0
        self.units_bet = 0
        self.salaries_paid = 0
        self.dividends_paid = 0
        self.asset_spending = 0
        self.total_salary = 0 # should be the same as dynamically calculated salaries_paid, just a sanity check
        self.price_exp = 30 * r() + 10 # the price we are ready to sell at
        self.census_ = None # census object is connected when census_ is initialized

    def __str__(self):
        return '-' * 10 + '\nProducer print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10
    
    def reset_day(self): # reset all the day-to-day variables
        self.revenue = 0
        self.salaries_paid = 0
        self.dividends_paid = 0
        self.asset_spending = 0
        self.units_sold = 0

    def depreciate_goods(self):
        for good_ID in self.stored_goods:
            self.stored_goods[good_ID] = self.goods[good_ID].depreciate(self.stored_goods[good_ID])

    def make_production_plan(self): # RETURNS THE NUMBER OF UNITS WE WISH TO PRODUCE; for now -> max value possible
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        num_units = 0
        while self.check_production_plan(num_units+1):
            num_units += 1
        return num_units

    def check_production_plan(self, num_units): # make sure we can produce the suggested number of units
        if self.productivity(self.total_skill) < num_units:
            return False
        for good_ID in self.components:
            if self.stored_goods[good_ID] < self.components[good_ID] * num_units:
                return False
        return True

    def produce_good(self): # produce the amount of goods suggested in the production plan
        self.cash -= self.fixed_cost
        num_units = self.make_production_plan()
        if not self.check_production_plan(num_units):
            return
        for good_ID in self.components:
            comp = self.components[good_ID]
            needed_comp = comp * num_units
            self.stored_goods[good_ID] -= needed_comp
        self.stored_goods[self.good_ID] += num_units

    def pay_salary(self): # pay salary to all current employees
        for emp_ID, (emp, salary) in self.employees.items():
            self.cash -= salary
            emp.earn_salary()
            self.salaries_paid += salary

    def request_good_offer(self): # refer to consumer class function
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        ans = []
        prod_price = self.price_exp
        front_prod = self.productivity(self.total_skill)
        old_prices = self.census_.stats['goods_market_prices'][self.census_.time-1]
        needed_quant = {}
        total_price = 0
        for good_ID, need in self.components.items():
            price = old_prices[good_ID][0] # this is market price
            must_have = front_prod * need
            must_have_after_depr = must_have
            quant = int(must_have_after_depr - self.stored_goods[good_ID] + 1)
            if quant <= 0:
                continue
            needed_quant[good_ID] = (quant, price)
            total_price += quant * price
        total_price += self.total_salary
        total_revenue = prod_price * front_prod
        for good_ID, (quant, price) in needed_quant.items():
            rest_total = total_price - quant * price
            rest_for_comp = max(total_revenue - rest_total, 10)
            rest_for_comp *= 0.9 + 0.1 * r()
            upd_price = rest_for_comp / quant
            ans.append((good_ID, upd_price, quant))
        return ans

    def verify_good_buyer(self, offers): # verify the offer (buyer side)
        return all([price*quant <= self.cash for good_ID, price, quant in offers])
    
    def purchase_good(self, good_ID, quant, price):
        self.cash -= quant * price
        self.stored_goods[good_ID] += quant
        self.asset_spending += quant * price
    
    def create_good_offer(self): # create sell offers for the goods market, same format as request_good_offer
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        price = self.price_exp
        quant = int(self.stored_goods[self.good_ID])
        self.units_bet = quant
        return [(self.good_ID, price, quant)] if quant > 0 else []

    def verify_good_seller(self, offers): # verify the offer (seller side)
        plan_to_sell = {}
        for good_ID, price, quant in offers:
            if not good_ID in plan_to_sell:
                plan_to_sell[good_ID] = 0
            plan_to_sell[good_ID] += quant
        for good_ID, quant in plan_to_sell.items():
            if quant > self.stored_goods[good_ID]:
                return False
        return True

    def sell_good(self, good_ID, quant, price):
        self.cash += quant * price
        self.stored_goods[good_ID] -= quant
        self.revenue += quant * price
        self.units_sold += quant
    
    def calc_price_exp(self):
        # actual to ideal spending ratio
        ratio = (self.units_sold + 1) / (self.units_bet + 1)
        # make it a bit more conservative (tends to the mean)
        ratio = ratio * 1/2 + 1/2 + (0.1 if ratio > 0.95 else 0) + (0.2 if self.units_bet == 0 else 0)
        # big ratio -> we should have smaller price, small ratio -> bigger price
        self.price_exp *= (0.95 + 0.1 * r()) * ratio

    def staff_strategy(self): # fire some employees, request employees on the labor market; return [(skill, salary), ...]
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        ans = []
        old_prod = self.productivity(self.total_skill)
        old_prices = self.census_.stats['goods_market_prices'][self.census_.time-1]
        gross = 0 # the cost to produce one unit
        for good_ID, (avg, _, _, _, _) in old_prices.items():
            if avg == -1:
                avg = r() * 30 + 30
            if good_ID == self.good_ID:
                gross += avg
            elif good_ID in self.components:
                gross -= avg * self.components[good_ID]
        # fire old employees
        for emp_ID, (emp, salary) in list(self.employees.items()):
            prod_drop = old_prod - self.productivity(self.total_skill - emp.skill)
            marginal_value = prod_drop * gross # how much this employee contributes
            if marginal_value > salary: # we lose money on this employee! Fire them!
                self.fire_employee(emp_ID)
        # hire new employees
        for i in range(1, 10):
            new_prod = self.productivity(self.total_skill + i)
            prod_change = new_prod - old_prod
            coef = 0.8 + r() * 0.2
            salary = prod_change * gross * coef
            ans.append((i, salary))
        return ans

    def hire_employee(self, employee, salary):
        self.employees[employee.ID] = (employee, salary)
        self.total_skill += employee.skill
        self.total_salary += salary
        employee.get_hired(self, salary)

    def fire_employee(self, emp_ID):
        employee, salary = self.employees.pop(emp_ID)
        employee.get_fired()
        self.total_skill -= employee.skill
        self.total_salary -= salary
    
    def market_asset_evaluation(self): # calculates market value of all the non-cash assets
        total = 0
        price_dict = self.census_.stats['goods_market_prices'][self.census_.time]
        for good_ID, num in self.stored_goods.items():
            price = max(price_dict[good_ID][0], 0)
            total += price * num
        return total
    
    def dividend_policy(self):
        income = self.revenue - self.fixed_cost - self.salaries_paid - self.asset_spending
        return max(income / 10, 0)

    def pay_dividends(self):
        div = self.dividend_policy()
        for cons_ID, (cons, stocks) in self.ownership.items():
            payment = stocks / self.stocks * div
            self.cash -= payment
            self.dividends_paid += payment
            cons.earn_dividends(payment)

    def make_log(self): # logging
        return {
            'prod_ID': self.ID,
            'good ID': self.good_ID,
            'revenue': self.revenue,
            'fixed cost': self.fixed_cost,
            'salaries paid': self.salaries_paid,
            'assets spending': self.asset_spending,
            'income': self.revenue - self.fixed_cost - self.salaries_paid - self.asset_spending,
            'dividends': self.dividends_paid,
            'retained': self.revenue - self.fixed_cost - self.salaries_paid - self.asset_spending - self.dividends_paid,
            'no-cash assets value': self.market_asset_evaluation(),
            'cash': self.cash,
            'units sold': self.units_sold,
            'time': self.census_.time
        }


class census(): # meant to easily calculate any metrics for the market (to start with, salary expectation)

    def __init__(self, goods, consumers, producers, g_market, l_market):
        self.goods = goods
        self.consumers = consumers
        self.producers = producers
        self.g_market = g_market
        self.l_market = l_market
        self.stats = {'goods_market_prices': g_market.trans_arch, 'salary_skill_ratio': 30.0} # here we can store any statistics we wish
        self.time = 0
        # connect census_ to other objects
        for cons_ID, cons in consumers.items():
            cons.census_ = self
        for prod_ID, prod in producers.items():
            prod.census_ = self
        g_market.census_ = self
        l_market.census_ = self

    def __str__(self):
        return '-' * 10 + '\nCensus print out:\n' + '\n'.join([key + ':\n' + str(val) 
                                                               for key, val in self.stats.items()]) + '\nTime: ' + str(self.time) + '\n' + '-' * 10

    def salary_skill_ratio(self): # calculate salary / skill ratio of the current market
        tot_sal = 30
        tot_skill = 1
        for cons_id, cons in self.consumers.items():
            if cons.job is not None:
                tot_sal += cons.job[1]
                tot_skill += cons.skill
        self.stats['salary_skill_ratio'] = tot_sal / tot_skill
    
    def reset_day(self, time):
        self.salary_skill_ratio()
        self.time = time
        self.file.write('DAY ' + str(time) + ' STARTED\n')


class simulation():

    def __init__(self, consumers, producers, goods, g_market, l_market, census_):
        self.consumers = consumers
        self.producers = producers
        self.goods = goods
        self.l_market = l_market
        self.g_market = g_market
        self.census_ = census_

    def run(self, tot_time): # the 'run' button of the simulation
        self.start_simulation()
        for time in range(1, tot_time+1):
            self.run_cycle(time)
        self.finish_simulation()

    def start_simulation(self): # some needed initializations before we start the simulation
        # creating dummy consumer and producer
        bob = consumer(-1, lambda x: 0, 0, 0, self.goods)
        tesla = producer(-1, 0, 'bruh', 0, lambda x: 0, {}, bob, 10, self.goods)
        bob.census_ = self.census_
        tesla.census_ = self.census_
        # generating day zero fake data
        self.g_market.fake_data()
        # creating dataframes for logging
        self.df_gmarket = pd.DataFrame(columns=list(self.g_market.make_log()[0].keys()))
        self.df_cons = pd.DataFrame(columns=list(bob.make_log().keys()))
        self.df_prod = pd.DataFrame(columns=list(tesla.make_log().keys()))
        # create a file for the redundant output
        self.census_.file = open('output.txt', 'w')

    def finish_simulation(self): # wrapping up the simulation and saving results
        self.df_cons.to_csv('consumers.csv', index=False, float_format='%.2f')
        self.df_prod.to_csv('producers.csv', index=False, float_format='%.2f')
        self.df_gmarket.to_csv('goods_market.csv', index=False, float_format='%.2f')
        self.census_.file.close()
    
    def run_cycle(self, time): # run one cycle of the simulation
        # step one - reset the day
        self.reset_day(time)
        # step two - produce goods and pay salary
        self.produce()
        # step three - trade goods
        self.trade_goods()
        # step four - trade labor
        self.trade_labor()
        # step five - pay dividends and trade stocks (to be implemented)
        self.trade_stocks()
        # step six - save logging
        self.logging()
        # step seven - goods depreciation
        self.depreciate()
    
    def reset_day(self, time): # step one
        for cons_ID, cons in self.consumers.items():
                cons.reset_day()
        for prod_ID, prod in self.producers.items():
            prod.reset_day()
        self.l_market.reset_day()
        self.g_market.reset_day()
        self.census_.reset_day(time)
    
    def produce(self): # step three
        for prod_ID, prod in self.producers.items():
            prod.produce_good()
            prod.pay_salary()
    
    def trade_goods(self): # step four
        for prod_ID, prod in self.producers.items():
            self.g_market.add_offer_sell(prod.create_good_offer(), prod)
        self.g_market.sort_offers()
        self.g_market.run_day()
        for cons_ID, cons in self.consumers.items(): # maybe move to a different phase???
            cons.calc_coins_for_util() # update the util to coins weights
        for prod_ID, prod in self.producers.items():
            prod.calc_price_exp()
    
    def trade_labor(self): # step five
        for prod_ID, prod in self.producers.items(): # producers go first so that fired consumers would have a chance to find a new job
            for skill, salary in prod.staff_strategy():
                self.l_market.add_giver(prod, skill, salary)
        for cons_ID, cons in self.consumers.items():
            bet = cons.request_job_offer()
            if bet == 0: # not interested
                continue
            self.l_market.add_taker(cons, bet)
        for cons_ID, cons in self.consumers.items():
            cons.calc_salary_expectation()
        self.l_market.run_day()
    
    def trade_stocks(self): # step six -> later would add actual stock trades
        for prod_ID, prod in self.producers.items():
            prod.pay_dividends()

    def logging(self): # step seven
        # goods market logging must happen before others
        self.df_gmarket = pd.concat([self.df_gmarket, pd.DataFrame(self.g_market.make_log())])
        for cons_ID, cons in self.consumers.items():
            self.df_cons = pd.concat([self.df_cons, pd.DataFrame.from_dict(cons.make_log(), orient='index').T])
        for prod_ID, prod in self.producers.items():
            self.df_prod = pd.concat([self.df_prod, pd.DataFrame.from_dict(prod.make_log(), orient='index').T])
    
    def depreciate(self): # step two
        for cons_ID, cons in self.consumers.items():
            cons.depreciate_goods()
        for prod_ID, prod in self.producers.items():
            prod.depreciate_goods()
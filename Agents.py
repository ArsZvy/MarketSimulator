import pandas as pd
from random import random as r, sample, shuffle


class good():

    def __init__(self, ID, depreciation, consumption):
        self.ID = ID # ID of a good
        self.depr_rate = depreciation # depreciation rate
        self.cons_rate = consumption # consumption rate

    def depreciate(self, quant):
        eps = 0.000001
        return max(0, quant - self.depr_rate * int(quant + 1 - eps)) # calculate # of goods, depreciate each of them

    def consume(self, quant):
        eps = 0.000001
        return max(0, quant - self.cons_rate * int(quant + 1 - eps)) # calculate # of goods, consume each of them


class goods_market():

    def __init__(self):
        self.name = 'goods' # name of a market: "goods", "labor", "real estate", "stock exchange" etc
        self.goods = None
        self.consumers = None
        self.producers = None
        self.spread = {} # stores sell offers: {good_ID: [(price, quantity, seller), ...]}
        self.trans_arch = {} # archieve of statistics of daily transactions: {time: {good_ID: (avg, std, min_price, max_price, items sold)}}
        self.trans_today = {} # transactions that happen today
        self.offered_today = {}
        self.census_ = None # census object is connected when census_ is initialized
    
    def __str__(self):
        return '-' * 10 + '\nGoods market print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10

    def fake_data(self): # generate fake data for day 0
        for good_ID in self.goods:
            avg_price = 100 * r() + 10
            self.trans_today[good_ID] = [(5, avg_price)]
            self.offered_today[good_ID] = 7
        self.calc_stat()

    def reset_day(self): # reset all the day-to-day variables
        self.spread = {}
        for good_ID in self.goods:
            self.spread[good_ID] = [[10**9, 0, None]] # list of sell offers, add the "barrier" offer that noone would ever take
            self.trans_today[good_ID] = []
            self.offered_today[good_ID] = 0

    def add_offer_sell(self, offers, seller): # add the offer to the spread
        if not seller.verify_good_seller(offers): # if not valid offer list -> do not add it
            return
        for good_ID, price, quant in offers:
            self.spread[good_ID].append([price, quant, seller])
            self.offered_today[good_ID] += quant

    def sort_offers(self):
        for good_ID, cur_spread in self.spread.items():
            cur_spread.sort(key=lambda x: x[0])

    def find_offer(self, buyer): # tries to match buyer with some sell offer; return True if some transaction has happened
        done = False
        offers = buyer.request_good_offer()
        if not buyer.verify_good_buyer(offers):
            return False
        shuffle(offers)
        for good_ID, buy_price, buy_quant in offers:
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
    
    def reflect_day(self):
        self.calc_stat()
    
    def asset_market_evaluation(self, stored_goods): # market evaluation of someone's assets
        total = 0
        price_dict = self.trans_arch[self.census_.time]
        for good_ID, num in stored_goods.items():
            price = price_dict[good_ID][0] if price_dict[good_ID][4] != 0 else 0
            total += price * num
        return total
        
    def make_log(self): # logging process
        stat = self.trans_arch[self.census_.time]
        return [{
            'good ID': good_ID,
            'avg price': prices[0],
            'std price': prices[1],
            'min price': prices[2],
            'max price': prices[3],
            'items sold': prices[4],
            'items offered': self.offered_today[good_ID],
            'time': self.census_.time
        } for good_ID, prices in stat.items()]


class labor_market():

    def __init__(self):
        self.name = 'labor' # name of a market: "goods", "labor", "real estate", "stock exchange" etc
        self.consumers = None
        self.producers = None
        self.candidates = 0 # needed for logging
        self.positions = 0
        self.hired = 0
        self.tot_sal = 0
        self.tot_skill = 0
        self.census_ = None # census object is connected when census_ is initialized

    def reset_day(self):
        self.job_takers = set() # future employees
        self.job_givers = set() # future employers
        self.candidates = 0
        self.positions = 0
        self.hired = 0
        self.tot_sal = 0
        self.tot_skill = 0

    def add_taker(self, cons, salary):
        self.job_takers.add((cons.skill, salary, cons.ID))
        self.candidates += 1

    def add_giver(self, prod, skill, salary):
        self.job_givers.add((skill, salary, prod.ID))
        self.positions += 1

    def run_day(self): # run the whole hiring cycle, FOR NOW EXTREMELY INEFFICIENT O(n^2), IDK HOW TO IMPROVE IT LOL
        self.census_.file.write('Started the day of trades (labor)!\n')
        self.census_.file.write('Job takers (skill, salary, ID)\n')
        self.census_.file.write(str(self.job_takers) + '\n')
        self.census_.file.write('Job givers\n')
        self.census_.file.write(str(self.job_givers) + '\n')
        for job_taker in self.job_takers:
            for job_giver in self.job_givers:
                if job_taker[0] >= job_giver[0] and job_taker[1] <= job_giver[1]: # skillful enough and not too expensive -> hire
                    self.hired += 1
                    self.job_givers.remove(job_giver)
                    salary = (job_taker[1] + job_giver[1]) / 2
                    self.tot_sal += salary
                    self.tot_skill += job_taker[0]
                    employee = self.consumers[job_taker[2]]
                    employer = self.producers[job_giver[2]]
                    if employee.job is not None:
                        old_empl = employee.job[0]
                        old_empl.fire_employee(employee.ID)
                    self.census_.file.write(' '.join(map(str, ['Got a match (employer_ID, employee_ID, salary):', employer.ID, employee.ID, salary])) + '\n')
                    employer.hire_employee(employee, salary)
                    break
    
    def make_log(self):
        return {
            'candidates': self.candidates,
            'positions': self.positions,
            'hired': self.hired,
            'avg hired salary': self.tot_sal / self.hired if self.hired > 0 else -1,
            'avg hired skill': self.tot_skill / self.hired if self.hired > 0 else -1,
            'time': self.census_.time
        }


class consumer():
    
    def __init__(self, ID, util, cash, skill):
        self.ID = ID # ID of a consumer
        self.goods = None
        self.util = util # {good_ID : #} -> utils (a function that takes dict of goods utility)
        self.cash = cash # cash assets
        self.stored_goods = {}
        self.skill = skill # skill (relevant for the job); later would make it a vector instead to represent different skills
        self.job = None # the job position of the type optional (employer, salary)
        self.spent_today = 0
        self.dividends = 0
        self.util_level = 0
        self.coins_for_util = 30 * (0.9 + 0.2*r()) # how much money are you willing to give for one util? Adjusted dynamically
        self.salary_expectation = 150 * (0.9 + 0.2*r()) # what is your expected salary? Adjusted dynamically
        self.census_ = None # census object is connected when census_ is initialized
    
    def __str__(self):
        return '-' * 10 + '\nConsumer print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10

    def reset_day(self): # reset all the day-to-day variables
        self.spent_today = 0
        self.dividends = 0
        self.util_level = 0

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

    def request_good_offer(self): # RETURN THE MAX PRICES FOR THE GOODS WE ARE READY TO PURCHASE: [(good_ID, price, quant), ...]
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        grads = self.util_grad()
        ans = []
        for good_ID in grads:
            adj_coef = min(0.2 + self.goods[good_ID].depr_rate + self.goods[good_ID].cons_rate, 1) # adjust for good durability
            if grads[good_ID] > 0:
                price_bet = min(grads[good_ID] * self.coins_for_util / adj_coef, self.cash-30)
                if price_bet < 0:
                    continue
                if self.spent_today > (2 * self.job[1] if self.job is not None else self.cash / 5):
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
        # if already employed, search for the job if your salary expectation is significantly higher than your current job salary
        if self.job is not None and self.salary_expectation / self.job[1] < 1.2: 
            return 0
        return self.salary_expectation

    def get_fired(self):
        self.job = None

    def get_hired(self, employer, salary): # details in the labor market
        self.job = (employer, salary) # tuple of employer (class producer) and salary

    def earn_dividends(self, payment):
        self.cash += payment
        self.dividends += payment

    def consume_goods(self): # consume all the goods
        self.util_level = self.util(self.stored_goods)
        for good_ID, amount in self.stored_goods.items():
            self.stored_goods[good_ID] = self.goods[good_ID].consume(amount)
    
    def depreciate_goods(self):
        for good_ID, amount in self.stored_goods.items():
            self.stored_goods[good_ID] = self.goods[good_ID].depreciate(amount)

    def calc_coins_for_util(self):
        # actual to ideal spending ratio
        okay_to_spend = min(self.job[1], self.cash / 10) if self.job is not None else self.cash / 10
        ratio = (okay_to_spend + 30) / (self.spent_today + 30)
        # make it a bit more conservative (tends to the mean)
        ratio = ratio * 1/3 + 2/3
        # big ratio -> we should have bigger util value
        self.coins_for_util *= ratio

    def calc_salary_expectation(self):
        market_salary = self.census_.stats['salary_skill_ratio'] * self.skill
        update_coef = market_salary / self.salary_expectation * 1/2 + 1/2 # a little more conservative
        if self.job is None: # unemployed -> reduce your expectations
            if update_coef < 1: # our expectation is indeed too high
                self.salary_expectation *= update_coef * (0.95 + 0.1 * r())
            else: # beggers are no choosers, so reduce your expectations anyway
                self.salary_expectation *= (0.65 + 0.1 * r())
        else: # employed -> raise your expectations
            if update_coef < 1: # you are lucky! You are earning more than the market, so salary expectation barely changes
                self.salary_expectation *= (0.95 + 0.1 * r())
            else: # you are supposed to earn more according to the market survey!
                self.salary_expectation *= update_coef * (0.95 + 0.1 * r())
    
    def reflect_day(self):
        self.calc_coins_for_util()
        self.calc_salary_expectation()
    
    def make_log(self): # logging
        return {
            'cons_ID': self.ID,
            'cash': self.cash,
            'no-cash assets value': self.census_.g_market.asset_market_evaluation(self.stored_goods),
            'salary': self.job[1] if self.job is not None else 0,
            'dividends': self.dividends,
            'spending': self.spent_today,
            'utility': self.util_level,
            'skill': self.skill,
            'time': self.census_.time
        }


class producer():

    def __init__(self, ID, start_cap, good_ID, productivity, components, owner, stocks):
        self.ID = ID # company ID
        self.good_ID = good_ID # the good ID the company is producing
        self.goods = None
        self.productivity = productivity # function that maps # of hours to the number of units produced
        self.stored_goods = {} # stored goods
        self.cash = start_cap # the starting capital of the company
        self.components = components # {good_ID: #} -> number of each good needed to produce one unit of the desired good
        self.employees = {} # {consumer_ID: (consumer, salary)}
        self.stocks = stocks
        self.ownership = {owner.ID: (owner, stocks)}
        self.total_skill = 1
        self.revenue = 0
        self.units_sold = 0 # units sold in the round
        self.units_bet = 0 # units offered for sale in the round
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
        self.units_sold = 0
        self.units_bet = 0
        self.salaries_paid = 0
        self.dividends_paid = 0
        self.asset_spending = 0

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
        num_units = self.make_production_plan()
        if not self.check_production_plan(num_units):
            return
        for good_ID in self.components:
            comp = self.components[good_ID]
            needed_comp = comp * num_units
            needed_comp_after_prod = self.goods[good_ID].consume(needed_comp)
            delta = needed_comp - needed_comp_after_prod
            self.stored_goods[good_ID] -= delta
        self.stored_goods[self.good_ID] += num_units

    def pay_salary(self): # pay salary to all current employees
        for emp_ID, (emp, salary) in self.employees.items():
            self.cash -= salary
            emp.earn_salary()
            self.salaries_paid += salary
        assert abs(self.salaries_paid - self.total_salary) < 0.01 # this means our hiring process is fine

    def request_good_offer(self): # refer to consumer class function
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        eps = 0.000001
        ans = []
        prod_price = self.price_exp
        front_prod = self.productivity(self.total_skill)
        old_prices = self.census_.stats['goods_market_prices'][self.census_.time-1]
        needed_quant = {}
        total_price = 0
        for good_ID, need in self.components.items():
            price = old_prices[good_ID][0] # this is market price
            must_have = front_prod * need
            must_have_after = must_have
            while self.goods[good_ID].depreciate(must_have_after + 1) < must_have: # as the good would get depreciate, keep that in mind!
                must_have_after += 1
            quant = int(must_have_after - self.stored_goods[good_ID] + 1 - eps)
            if quant <= 0:
                continue
            needed_quant[good_ID] = (quant, price)
            total_price += quant * price
        total_price += self.total_salary
        total_revenue = prod_price * front_prod
        for good_ID, (quant, price) in needed_quant.items():
            rest_total = total_price - quant * price
            rest_for_comp = total_revenue - rest_total
            if rest_for_comp < 0:
                continue
            rest_for_comp *= 0.95 + 0.1 * r()
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
        if quant > self.productivity(self.total_skill): # do not just dump all your stored goods in the market
            quant = int(self.stored_goods[self.good_ID] * 1/5 + self.productivity(self.total_skill) * 4/5)
        self.units_bet = quant
        fifth = quant // 5
        mid = quant - fifth * 4
        if fifth == 0:
            return [(self.good_ID, price, quant)]
        return [(self.good_ID, price * 0.96, fifth), (self.good_ID, price * 0.98, fifth), (self.good_ID, price, mid),
                (self.good_ID, price * 1.02, fifth), (self.good_ID, price * 1.04, fifth)] if quant > 0 else []

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

    def staff_strategy(self): # fire some employees, request employees on the labor market; return [(skill, salary), ...]
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> excellent
        ans = []
        old_prod = self.productivity(self.total_skill)
        old_prices = self.census_.stats['goods_market_prices'][self.census_.time-1]
        gross = 0 # the cost to produce one unit
        for good_ID, (avg, _, _, _, _) in old_prices.items():
            if good_ID == self.good_ID:
                gross += avg
            elif good_ID in self.components:
                gross -= avg * self.components[good_ID]
        # fire old employees
        for emp_ID, (emp, salary) in list(self.employees.items()):
            prod_drop = old_prod - self.productivity(self.total_skill - emp.skill)
            marginal_value = prod_drop * gross # how much this employee contributes
            if marginal_value < salary * 0.9: # we lose too much money on this employee! Fire them!
                self.fire_employee(emp_ID)
        # hire new employees
        for i in sample(range(1, 10), 3):
            new_prod = self.productivity(self.total_skill + i)
            prod_change = new_prod - old_prod
            salary = prod_change * gross
            if salary > 0:
                ans.append((i, salary))
        return ans

    def hire_employee(self, employee, salary):
        self.employees[employee.ID] = (employee, salary)
        self.total_skill += employee.skill
        self.total_salary += salary
        employee.get_hired(self, salary)

    def fire_employee(self, emp_ID):
        employee, salary = self.employees.pop(emp_ID)
        self.total_skill -= employee.skill
        self.total_salary -= salary
        employee.get_fired()
    
    def dividend_policy(self):
        income = self.revenue - self.salaries_paid - self.asset_spending
        return max(income / 2, 0)

    def pay_dividends(self):
        div = self.dividend_policy()
        self.cash -= div
        self.dividends_paid = div
        for cons_ID, (cons, stocks) in self.ownership.items():
            payment = stocks / self.stocks * div
            cons.earn_dividends(payment)

    def depreciate_goods(self):
        for good_ID, amount in self.stored_goods.items():
            self.stored_goods[good_ID] = self.goods[good_ID].depreciate(amount)

    def calc_price_exp(self):
        # actual to ideal spending ratio
        ratio = (self.units_sold + 1) / (self.units_bet + 1)
        # make it a bit more conservative (tends to the mean)
        ratio = ratio * 1/5 + 4/5
        if ratio > 0.98 and self.units_sold != 0: # sold out -> increase price
            ratio += 0.05
        if self.units_bet == 0: # we did not even produce anything -> increase price expectation to boost production incentive
            ratio += 0.1
        if self.units_sold == 0 and self.units_bet != 0: # we did not sell anything -> drop prices
            ratio -= 0.05
        # big ratio -> bigger price, small ratio -> smaller price
        self.price_exp *=  ratio
    
    def reflect_day(self):
        self.calc_price_exp()

    def bankrupt(self):
        if self.cash < 0:
            for emp_ID in list(self.employees.keys()):
                self.fire_employee(emp_ID)
            return True
        return False

    def make_log(self): # logging
        return {
            'prod_ID': self.ID,
            'good ID': self.good_ID,
            'revenue': self.revenue,
            'salaries paid': self.salaries_paid,
            'assets spending': self.asset_spending,
            'income': self.revenue - self.salaries_paid - self.asset_spending,
            'dividends': self.dividends_paid,
            'retained': self.revenue - self.salaries_paid - self.asset_spending - self.dividends_paid,
            'no-cash assets value': self.census_.g_market.asset_market_evaluation(self.stored_goods),
            'cash': self.cash,
            'units sold': self.units_sold,
            'units offered': self.units_bet,
            'price exp': self.price_exp,
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
            cons.goods = goods
        for prod_ID, prod in producers.items():
            prod.census_ = self
            prod.goods = goods
        g_market.census_ = self
        g_market.goods = goods
        g_market.consumers = consumers
        g_market.producers = producers
        l_market.census_ = self
        l_market.consumers = consumers
        l_market.producers = producers
        for good_ID in goods: # it is needed to correctly start the simulation (look start_simulation)
            g_market.trans_today[good_ID] = []
            for cons_ID, cons in consumers.items():
                cons.stored_goods[good_ID] = 0
            for prod_ID, prod in producers.items():
                prod.stored_goods[good_ID] = 0

    def __str__(self):
        return '-' * 10 + '\nCensus print out:\n' + '\n'.join([key + ':\n' + str(val) 
                                                               for key, val in self.stats.items()]) + '\nTime: ' + str(self.time) + '\n' + '-' * 10
    
    def reset_day(self, time):
        self.time = time
        self.file.write('DAY ' + str(time) + ' STARTED\n')

    def calc_salary_skill_ratio(self): # calculate salary / skill ratio of the current market
        tot_sal = 30
        tot_skill = 1
        for cons_id, cons in self.consumers.items():
            if cons.job is not None:
                tot_sal += cons.job[1]
                tot_skill += cons.skill
        self.stats['salary_skill_ratio'] = tot_sal / tot_skill
    
    def reflect_day(self):
        self.calc_salary_skill_ratio


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
        bob = self.consumers[0]
        tesla = self.producers[0]
        # generating day zero fake data
        self.g_market.fake_data()
        # creating dataframes for logging
        self.df_gmarket = pd.DataFrame(columns=list(self.g_market.make_log()[0].keys()))
        self.df_lmarket = pd.DataFrame(columns=list(self.l_market.make_log().keys()))
        self.df_cons = pd.DataFrame(columns=list(bob.make_log().keys()))
        self.df_prod = pd.DataFrame(columns=list(tesla.make_log().keys()))
        # create a file for the redundant output
        self.census_.file = open('output.txt', 'w')

    def finish_simulation(self): # wrapping up the simulation and saving results
        self.df_cons.to_csv('consumers.csv', index=False, float_format='%.2f')
        self.df_prod.to_csv('producers.csv', index=False, float_format='%.2f')
        self.df_gmarket.to_csv('goods_market.csv', index=False, float_format='%.2f')
        self.df_lmarket.to_csv('labor_market.csv', index=False, float_format='%.2f')
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
        # step six - goods consumption and depreciation
        self.consume_depreciate()
        # step seven - reflect on the current day
        self.reflect_day()
        # step eight - bankruptcy (and registration of new companies -> later)
        self.bankruptcy()
        # step nine - save logging
        self.logging()
    
    def reset_day(self, time): # step one
        for cons_ID, cons in self.consumers.items():
                cons.reset_day()
        for prod_ID, prod in self.producers.items():
            prod.reset_day()
        self.l_market.reset_day()
        self.g_market.reset_day()
        self.census_.reset_day(time)
    
    def produce(self): # step two
        for prod_ID, prod in self.producers.items():
            prod.produce_good()
            prod.pay_salary()
    
    def trade_goods(self): # step three
        for prod_ID, prod in self.producers.items():
            self.g_market.add_offer_sell(prod.create_good_offer(), prod)
        self.g_market.sort_offers()
        self.g_market.run_day()
    
    def trade_labor(self): # step four
        for prod_ID, prod in self.producers.items(): # producers go first so that fired consumers would have a chance to find a new job
            for skill, salary in prod.staff_strategy():
                self.l_market.add_giver(prod, skill, salary)
        for cons_ID, cons in self.consumers.items():
            bet = cons.request_job_offer()
            if bet == 0: # not interested
                continue
            self.l_market.add_taker(cons, bet)
        self.l_market.run_day()
    
    def trade_stocks(self): # step five -> later would add actual stock trades
        for prod_ID, prod in self.producers.items():
            prod.pay_dividends()

    def consume_depreciate(self): # step six
        for cons_ID, cons in self.consumers.items():
            cons.consume_goods()
            cons.depreciate_goods()
        for prod_ID, prod in self.producers.items():
            prod.depreciate_goods()
        
    def reflect_day(self): # step seven
        self.census_.reflect_day() # should go first
        self.g_market.reflect_day()
        for cons_ID, cons in self.consumers.items():
            cons.reflect_day()
        for prod_ID, prod in self.producers.items():
            prod.reflect_day()

    def bankruptcy(self): # step eight -> to add liquidation of the company later
        for prod_ID, prod in list(self.producers.items()):
            if prod.bankrupt():
                self.producers.pop(prod_ID)

    def logging(self): # step nine
        self.df_gmarket = pd.concat([self.df_gmarket, pd.DataFrame(self.g_market.make_log())])
        self.df_lmarket = pd.concat([self.df_lmarket, pd.DataFrame.from_dict(self.l_market.make_log(), orient='index').T])
        for cons_ID, cons in self.consumers.items():
            self.df_cons = pd.concat([self.df_cons, pd.DataFrame.from_dict(cons.make_log(), orient='index').T])
        for prod_ID, prod in self.producers.items():
            self.df_prod = pd.concat([self.df_prod, pd.DataFrame.from_dict(prod.make_log(), orient='index').T])
            
import pandas as pd
from random import random as r, sample, shuffle


class good():

    def __init__(self, ID, depreciation, consumption, good_type):
        self.type = good_type
        self.ID = ID # ID of a good
        self.depr_rate = depreciation # depreciation rate
        self.cons_rate = consumption # consumption rate

    def depreciate(self, quant):
        res = quant - self.depr_rate * quant
        return res if res > 0.1 else 0

    def consume(self, quant):
        res = quant - self.cons_rate * quant
        return res

class goods_market():

    def __init__(self):
        # permanent variables
        self.name = 'goods' # name of a market: "goods", "labor", "real estate", "stock exchange" etc
        self.census_ = None # census object is connected when census_ is initialized
        # resettable variables
        self.spread = {} # stores sell offers: {good_ID: [(price_buyer, quantity, seller, price), ...]}
        self.stats = {} # archieve of statistics of daily transactions: {time: {good_ID: (avg, std, min_price, max_price, items sold)}}
        self.trans_today = {} # transactions that happen today
        self.offered_today = {}
        self.spread_public = {}
    
    def __str__(self):
        return '-' * 10 + '\nGoods market print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10

    def fake_data(self): # generate pseudo-random fake data for day 0
        for good_ID in self.goods:
            avg_price = 100 * r() + 10
            self.trans_today[good_ID] = [(5, avg_price, 0.1)]
            self.offered_today[good_ID] = 7
        self.calc_stat()

    def reset_day(self): # reset all the day-to-day variables
        self.spread = {}
        for good_ID in self.goods:
            if self.goods[good_ID].type:
                self.spread[good_ID] = [[10**9, 0, None, 10**9]] # list of sell offers, add the "barrier" offer that noone would ever take
            else:
                self.spread_public[good_ID] = [[10**9, 0, None, 10**9]]
            self.trans_today[good_ID] = []
            self.offered_today[good_ID] = 0

    def add_offer_sell(self, offers, seller): # add the offer to the spread
        if not seller.verify_good_seller(offers): # if not valid offer list -> do not add it
            return
        for good_ID, price, quant in offers:
            # UPDATE PRICE FOR TAXATION
            add_tax = self.gov.trans_taxes[good_ID](price)
            price_buyer = price + add_tax
            self.offered_today[good_ID] += quant
            if self.goods[good_ID].type: # market of private goods -> trades with everyone
                self.spread[good_ID].append([price_buyer, quant, seller, price])
            else:
                self.spread_public[good_ID].append([price_buyer, quant, seller, price])

    def sort_offers(self):
        for good_ID, cur_spread in self.spread.items():
            cur_spread.sort(key=lambda x: x[0])
        for good_ID, cur_spread in self.spread_public.items():
            cur_spread.sort(key=lambda x: x[0])

    def find_offer(self, buyer): # tries to match buyer with some sell offer; return True if some transaction has happened
        done = False
        offers = buyer.request_good_offer()
        if not buyer.verify_good_buyer(offers):
            return False
        shuffle(offers)
        for good_ID, buy_price, buy_quant in offers:
            is_private = self.goods[good_ID].type
            sell_price_tax, sell_quant, seller, sell_price_notax = self.spread[good_ID][0] if is_private else self.spread_public[good_ID][0]
            self.census_.file.write(' '.join(map(str, ['Deal under consideration (good_ID, sell_price_tax, sell_price_notax, sell_quant, buy_price, buy_quant):', 
                                                       good_ID, sell_price_tax, sell_price_notax, sell_quant, buy_price, buy_quant]))+'\n')
            if buy_price >= sell_price_tax:
                self.census_.file.write('Deal accepted\n')
                done = True
                trans_quant = min(buy_quant, sell_quant)
                if trans_quant == sell_quant:
                    self.spread[good_ID].pop(0) if is_private else self.spread_public[good_ID].pop(0)
                else:
                    if is_private:
                        self.spread[good_ID][0][1] -= trans_quant
                    else:
                        self.spread_public[good_ID][0][1] -= trans_quant
                seller.sell_good(good_ID, trans_quant, sell_price_notax)
                buyer.purchase_good(good_ID, trans_quant, sell_price_tax)
                taxed_amount = (sell_price_tax - sell_price_notax) * trans_quant
                self.gov.receive_trans_tax(taxed_amount)
                self.trans_today[good_ID].append((trans_quant, sell_price_tax, taxed_amount))
                break
        return done

    def run_day(self): # here we actually run the day of trades
        self.census_.file.write('Started the day of trades (goods)!\n')
        # trading private goods (with consumers and producers)
        all_IDs = [(key, 0) for key in self.consumers.keys()] + [(key, 1) for key in self.producers.keys()]
        all_set = set(sample(all_IDs, len(all_IDs)))
        while len(all_set) > 0:
            cur_ID, cur_type = all_set.pop()
            cur_buyer = self.consumers[cur_ID] if cur_type == 0 else self.producers[cur_ID]
            if self.find_offer(cur_buyer):
                all_set.add((cur_ID, cur_type))
        # trading public goods (with the government)
        while self.find_offer(self.gov):
            pass

    def calc_stat(self): # calculate (avg_price, std, avg_tax, min_price, max_price, items_sold) for each good_ID
        ans = {}
        for good_ID, trans_lst in self.trans_today.items():
            tot_sum, tot_num, tot_tax = 0, 0, 0
            min_price, max_price = 10**9, -1
            for quant, price, taxed in trans_lst:
                tot_sum += quant * price
                tot_num += quant
                tot_tax += taxed
                min_price = min(min_price, price)
                max_price = max(max_price, price)
            avg = tot_sum / tot_num if tot_num > 0 else -1
            avg_tax = tot_tax / tot_num if tot_num > 0 else 0
            tot_sqr = 0
            for quant, price, taxed in trans_lst:
                tot_sqr += quant * (price - avg)**2
            std = (tot_sqr / (tot_num - 1)) ** 0.5 if tot_num > 1 else -1
            if min_price == 10**9:
                min_price = -1
            if avg == -1:
                avg = self.stats[self.census_.time-1][good_ID]['avg_price_wtax']
            ans[good_ID] = {}
            ans[good_ID]['avg_price_wtax'] = avg
            ans[good_ID]['std_price'] = std
            ans[good_ID]['avg_tax'] = avg_tax
            ans[good_ID]['min_price'] = min_price
            ans[good_ID]['max_price'] = max_price
            ans[good_ID]['items_sold'] = tot_num
            ans[good_ID]['items_offered'] = self.offered_today[good_ID]
        self.stats[self.census_.time] = ans
    
    def reflect_day(self):
        self.calc_stat()
    
    def asset_market_evaluation(self, stored_goods): # market evaluation of someone's assets
        total = 0
        price_dict = self.stats[self.census_.time]
        for good_ID, num in stored_goods.items():
            price = price_dict[good_ID]['avg_price_wtax'] if price_dict[good_ID]['items_sold'] != 0 else 0
            total += price * num
        return total
        
    def make_log(self): # logging process
        time = self.census_.time
        ans = []
        for good_ID, cur_stat in self.stats[time].items():
            log_row = cur_stat.copy()
            log_row['good_ID'] = good_ID
            log_row['time'] = time
            ans.append(log_row)
        return ans


class labor_market():

    def __init__(self):
        # permanent variables
        self.name = 'labor' # name of a market: "goods", "labor", "real estate", "stock exchange" etc
        self.stats = {}
        self.census_ = None # census object is connected when census_ is initialized
        # resettable variables
        self.candidates = 0 # needed for logging
        self.positions = 0
        self.hired = 0
        self.tot_sal = 0
        self.tot_skill = 0
    
    def fake_data(self):
        self.candidates = 4
        self.positions = 7
        self.hired = 3
        self.tot_sal = 250
        self.tot_skill = 18
        self.calc_stat()

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
                        old_empl.fire_employee([employee.ID])
                    self.census_.file.write(' '.join(map(str, ['Got a match (employer_ID, employee_ID, salary):', employer.ID, employee.ID, salary])) + '\n')
                    employer.hire_employee(employee, salary)
                    break
    
    def calc_stat(self):
        ans = {}
        ans['candidates'] = self.candidates
        ans['positions'] = self.positions
        ans['hired'] = self.hired
        ans['avg_hired_salary'] = self.tot_sal / self.hired if self.hired > 0 else -1
        ans['avg_hired_skill'] = self.tot_skill / self.hired if self.hired > 0 else -1
        ans['salary_skill_ratio'] = self.tot_sal / self.tot_skill if self.tot_skill > 0 else -1
        self.stats[self.census_.time] = ans
        
    def reflect_day(self):
        self.calc_stat()
    
    def make_log(self):
        log_row = self.stats[self.census_.time].copy()
        log_row['time'] = self.census_.time
        return log_row
    

class loans_market():

    def __init__(self):
        # permanent variables
        self.name = 'loans' # name of a market: "goods", "labor", "real estate", "stock exchange" etc
        self.census_ = None # census object is connected when census_ is initialized
        self.stats = {}
        # resettable variables
        self.spread = []
        # vars for statistics
        self.loans_gives_offered = 0 # agent gives money to the bank
        self.loans_takes_offered = 0 # agent takes money from the bank
        self.loans_gives_accepted = 0
        self.loans_takes_accepted = 0
        self.loans_gives_trans = [] # recorded transations
        self.loans_takes_trans = []
    
    def fake_data(self):
        self.loans_gives_trans.append((10, 0.1))
        self.loans_takes_trans.append((10, 0.1))
        self.calc_stat()

    def reset_day(self):
        self.spread = []
        self.loans_gives_offered = 0 # agent gives money to the bank
        self.loans_takes_offered = 0 # agent takes money from the bank
        self.loans_gives_accepted = 0
        self.loans_takes_accepted = 0
        self.loans_gives_trans = []
        self.loans_takes_trans = []
    
    def add_offer_loan(self, agent, details): # agent is an object, details is list of (gives, amount, period_payment, percentage)
        for offer in details:
            if offer[0]:
                self.loans_gives_offered += 1
            else:
                self.loans_takes_offered += 1
            self.spread.append((agent, offer))
    
    def run_day(self):
        self.census_.file.write('Started the day of trades (loans)\n')
        shuffle(self.spread)
        for agent, offer in self.spread:
            self.census_.file.write('Loan seeker (gives, amount, per_pay, perc): '+str(offer)+'\n')
            for bank_ID in sample(self.banks.keys(), len(self.banks)):
                bank = self.banks[bank_ID]
                if not bank.verify_loan_offer(agent, offer):
                    continue
                if not agent.verify_loan_offer(bank, offer):
                    continue
                self.census_.file.write('Got a match with bank '+str(bank_ID)+'\n')
                gives, amount, _, perc = offer
                if gives:
                    self.loans_gives_accepted += 1
                    self.loans_gives_trans.append((amount, perc))
                else:
                    self.loans_takes_accepted += 1
                    self.loans_takes_trans.append((amount, perc))
                bank.take_loan_offer(agent, offer)
                break
        
    def calc_stat(self):
        def find_vars(lst):
            tot_amount, tot_perc, num, min_perc, max_perc = 0, 0, 0, 100, -1
            for amount, perc in lst:
                tot_amount += amount
                tot_perc += perc
                num += 1
                min_perc = min(perc, min_perc)
                max_perc = max(perc, max_perc)
            return [tot_amount, tot_perc / num, min_perc, max_perc]
        # the format is: 
        # amount_gives, avg_perc_gives, min_perc_gives, max_perc_gives, amount_takes, avg_perc_takes, min_perc_takes, max_perc_takes
        ans = {}
        nums = find_vars(self.loans_gives_trans) + find_vars(self.loans_takes_trans)
        key_names = ['amount_gives', 'avg_perc_gives', 'min_perc_gives', 'max_perc_gives', 'amount_takes', 'avg_perc_takes', 'min_perc_takes', 'max_perc_takes']    
        for i in range(8):
            ans[key_names[i]] = nums[i]
        ans['loans_gives_offered'] = self.loans_gives_offered
        ans['loans_gives_accepted'] = self.loans_gives_accepted
        ans['loans_takes_offered'] = self.loans_takes_offered
        ans['loans_takes_accepted'] = self.loans_takes_accepted
        self.stats[self.census_.time] = ans
    
    def reflect_day(self):
        self.calc_stat()
    
    def make_log(self): # logging
        log_row = self.stats[self.census_.time].copy()
        log_row['time'] = self.census_.time
        return log_row


class consumer():
    
    def __init__(self, ID, util, util_public, cash, skill):
        # permanent variables
        self.ID = ID # ID of a consumer
        self.goods = None
        self.census_ = None # census object is connected when census_ is initialized
        self.util = util # {good_ID : #} -> utils (a function that takes dict of goods utility) FOR PRIVATE GOODS
        self.util_public = util_public
        self.cash = cash # cash assets
        self.stored_goods = {}
        self.skill = skill # skill (relevant for the job); later would make it a vector instead to represent different skills
        self.job = None # the job position of the type optional (employer, salary)
        # resettable variables
        self.spent_today = 0
        self.dividends = 0
        self.util_level = 0
        self.util_level_public = 0
        self.coins_for_util = 30 * (0.9 + 0.2*r()) # how much money are you willing to give for one util? Adjusted dynamically
        self.salary_expectation = 150 * (0.9 + 0.2*r()) # what is your expected salary? Adjusted dynamically
    
    def __str__(self):
        return '-' * 10 + '\nConsumer print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10

    def reset_day(self): # reset all the day-to-day variables
        self.spent_today = 0
        self.dividends = 0
        self.util_level = 0
        self.util_level_public = 0

    def earn_salary(self):
        salary = self.job[1] if self.job is not None else 0
        tax = self.gov.income_tax(salary)
        self.cash += salary - tax
        self.gov.receive_income_tax(tax)
    
    def util_grad(self): # return {good_ID: change in utility if you increase the good by one}
        eps = 1.0
        ans = {}
        util_old = self.util(self.stored_goods)
        for good_ID in self.goods:
            if not self.goods[good_ID].type:
                continue
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
    
    def pay_loan(self, payment):
        self.cash -= payment
        return (self.cash >= 0)
    
    def receive_loan(self, payment):
        self.cash += payment
    
    def create_loan_offer(self):  # return list of (gives, amount, period_payment, percentage)
        # this is a game-play function
        # baseline -> bad
        if r() > 0.02:
            return []
        c = self.cash
        return [(True, c / 10, c / 42, 0.02),
                (False, c / 10, c / 52, 0.03)]

    def verify_loan_offer(self, bank, offer):
        # this is a game-play function
        # baseline -> bad
        return True

    def consume_goods(self): # consume all the goods
        self.util_level = self.util(self.stored_goods)
        for good_ID, amount in self.stored_goods.items():
            self.stored_goods[good_ID] = self.goods[good_ID].consume(amount)
    
    def consume_goods_public(self, stored_public_goods): # consume public goods; takes goods dict -> return goods dict (remainder)
        self.util_level_public = self.util_public(stored_public_goods)
        rest = {}
        for good_ID, amount in stored_public_goods.items():
            rest[good_ID] = self.goods[good_ID].consume(amount)
        return rest
    
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
        market_salary = self.census_.stats['labor_market_stats'][self.census_.time-1]['salary_skill_ratio'] * self.skill
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
            'public_utility': self.util_level_public,
            'total utility': self.util_level + self.util_level_public,
            'skill': self.skill,
            'time': self.census_.time
        }


class producer():

    def __init__(self, ID, start_cap, good_ID, productivity, components, owner, stocks):
        # permanent variables
        self.ID = ID # company ID
        self.good_ID = good_ID # the good ID the company is producing
        self.goods = None
        self.census_ = None # census object is connected when census_ is initialized
        self.productivity = productivity # function that maps # of hours to the number of units produced
        self.stored_goods = {} # stored goods
        self.cash = start_cap # the starting capital of the company
        self.components = components # {good_ID: #} -> number of each good needed to produce one unit of the desired good
        self.employees = {} # {consumer_ID: (consumer, salary)}
        self.stocks = stocks
        self.ownership = {owner.ID: (owner, stocks)}
        self.total_skill = 1
        self.price_exp = 30 * r() + 10 # the price we are ready to sell at
        self.unit_net_price = 30 # the net value to produce one unit
        # resettable variables
        self.units_sold = 0 # units sold in the round
        self.units_bet = 0 # units offered for sale in the round
        # accounting variables
        self.revenue = 0
        self.salaries_paid = 0
        self.total_salary = 0 # should be the same as dynamically calculated salaries_paid, just a sanity check
        self.asset_spending = 0
        self.taxable_income = 0
        self.taxes_paid = 0
        self.income = 0
        self.dividends_paid = 0
        self.retained = 0

    def __str__(self):
        return '-' * 10 + '\nProducer print out:\n' + '\n'.join([key + ':\n' + str(val) for key, val in self.make_log().items()]) + '\n' + '-' * 10
    
    def reset_day(self): # reset all the day-to-day variables
        self.units_sold = 0
        self.units_bet = 0
        self.revenue = 0
        self.salaries_paid = 0
        self.asset_spending = 0
        self.taxable_income = 0
        self.taxes_paid = 0
        self.income = 0
        self.dividends_paid = 0
        self.retained = 0

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
        old_prices = self.census_.stats['goods_market_stats'][self.census_.time-1]
        needed_quant = {}
        total_price = 0
        for good_ID, need in self.components.items():
            price_tax = old_prices[good_ID]['avg_price_wtax'] # this is market price with taxes
            tax = old_prices[good_ID]['avg_tax'] # this is avg tax
            price = price_tax - tax
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
    
    def pay_taxes(self):
        self.taxable_income = self.revenue - self.salaries_paid - self.asset_spending
        taxes = self.gov.corp_tax(self.taxable_income)
        self.taxes_paid = taxes
        self.income = self.taxable_income - taxes
        self.cash -= taxes
        self.gov.receive_corp_tax(taxes)
    
    def fire_strategy(self): # return IDs of fired employees
        ans = []
        old_prod = self.productivity(self.total_skill)
        for emp_ID, (emp, salary) in list(self.employees.items()):
            prod_drop = old_prod - self.productivity(self.total_skill - emp.skill)
            marginal_value = prod_drop * self.unit_net_price # how much this employee contributes
            if marginal_value < salary * 0.9: # we lose too much money on this employee! Fire them!
                ans.append(emp_ID)
        return ans

    def hire_strategy(self): # return the offers for the labor market
        ans = []
        old_prod = self.productivity(self.total_skill)
        for i in sample(range(1, 10), 3):
            new_prod = self.productivity(self.total_skill + i)
            prod_change = new_prod - old_prod
            salary = prod_change * self.unit_net_price
            if salary > 0:
                ans.append((i, salary))
        return ans

    def fire_employee(self, emp_IDs): # takes a list of emp_IDs that need to be fired
        for emp_ID in emp_IDs:
            employee, salary = self.employees.pop(emp_ID)
            self.total_skill -= employee.skill
            self.total_salary -= salary
            employee.get_fired()

    def hire_employee(self, employee, salary):
        self.employees[employee.ID] = (employee, salary)
        self.total_skill += employee.skill
        self.total_salary += salary
        employee.get_hired(self, salary)
    
    def dividend_policy(self):
        return max(self.income / 2, 0)

    def pay_dividends(self):
        div = self.dividend_policy()
        self.cash -= div
        self.dividends_paid = div
        for cons_ID, (cons, stocks) in self.ownership.items():
            payment = stocks / self.stocks * div
            cons.earn_dividends(payment)
    
    def pay_loan(self, payment):
        self.cash -= payment
        return (self.cash >= 0)
    
    def receive_loan(self, payment):
        self.cash += payment
    
    def create_loan_offer(self): # return list of (gives, amount, period_payment, percentage)
        # this is a game-play strategy
        # baseline -> bad
        if r() > 0.05:
            return []
        c = self.cash
        return [(False, c / 20, c / 50, 0.03)]

    def verify_loan_offer(self, bank, offer):
        # this is a game-play function
        # baseline -> bad
        return True

    def depreciate_goods(self):
        for good_ID, amount in self.stored_goods.items():
            self.stored_goods[good_ID] = self.goods[good_ID].depreciate(amount)
    
    def calc_net_unit_price(self):
        old_prices = self.census_.stats['goods_market_stats'][self.census_.time]
        gross = 0 # the cost to produce one unit
        for good_ID in old_prices:
            avg = old_prices[good_ID]['avg_price_wtax']
            avg_tax = old_prices[good_ID]['avg_tax']
            avg_notax = avg - avg_tax
            if good_ID == self.good_ID:
                gross += avg_notax
            elif good_ID in self.components:
                gross -= avg * self.components[good_ID]
        self.unit_net_price = gross

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
        self.calc_net_unit_price()

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
    
class government():

    def __init__(self, corp_tax, income_tax, trans_taxes, cash=1000):
        # permanent variables
        self.name = 'government'
        self.corp_tax = corp_tax # function income -> tax
        self.income_tax = income_tax # function income -> tax
        self.trans_taxes = trans_taxes # dictionary: {good_ID: function trans_price -> tax}
        self.census_ = None # is initialized in census class
        self.cash = cash
        self.stored_public_goods = {}
        self.loan_rate = 0.01
        # resettable variables
        self.tax_collected_trans = 0
        self.tax_collected_income = 0
        self.tax_collected_corp = 0
        self.printed_money = 0
        self.spent_today = 0

    def reset_day(self):
        self.tax_collected_trans = 0
        self.tax_collected_income = 0
        self.tax_collected_corp = 0
        self.printed_money = 0
        self.spent_today = 0
    
    def receive_trans_tax(self, tax_amount):
        self.cash += tax_amount
        self.tax_collected_trans += tax_amount
    
    def receive_income_tax(self, tax_amount):
        self.cash += tax_amount
        self.tax_collected_income += tax_amount

    def receive_corp_tax(self, tax_amount):
        self.cash += tax_amount
        self.tax_collected_corp += tax_amount

    def request_good_offer(self): # RETURN THE MAX PRICES FOR THE GOODS WE ARE READY TO PURCHASE: [(good_ID, price, quant), ...]
        # THIS IS A GAME-PLAY FUNCTION
        # baseline -> bad
        offers = []
        for good_ID in self.goods:
            if not self.goods[good_ID].type:
                offers.append((good_ID, self.cash / 20, 1))
        return offers

    def verify_good_buyer(self, offers): # verify the offer (buyer side)
        return all([price*quant <= self.cash for good_ID, price, quant in offers])

    def purchase_good(self, good_ID, quant, price):
        self.cash -= quant * price
        self.stored_public_goods[good_ID] += quant
        self.spent_today += quant * price
    
    def pay_loan(self, payment):
        self.cash -= payment
        return True
    
    def receive_loan(self, payment):
        self.cash += payment
    
    def create_loan_offer(self):  # return list of (gives, amount, period_payment, percentage)
        # this is a game-play strategy
        # baseline -> bad
        return [(True, 100, 10, self.loan_rate),
                (False, 100, 10, self.loan_rate)]

    def verify_loan_offer(self, bank, offer):
        # this is a game-play function
        # baseline -> bad
        return True
    
    def consume_goods(self):
        stored = self.stored_public_goods
        consumed = {good_ID: 0 for good_ID in stored}
        for cons_ID, cons in self.consumers.items():
            rest = cons.consume_goods_public(stored)
            for good_ID in stored:
                consumed[good_ID] += stored[good_ID] - rest[good_ID]
        for good_ID in stored:
            stored[good_ID] = max(0, stored[good_ID] - consumed[good_ID])
    
    def depreciate_goods(self):
        for good_ID, amount in self.stored_public_goods.items():
            self.stored_public_goods[good_ID] = self.goods[good_ID].depreciate(amount)
    
    def update_loan_rate(self):
        pass

    def reflect_day(self):
        self.update_loan_rate()

    def make_log(self): # logging
        return {
            'budget': self.cash,
            'tax_collected_trans': self.tax_collected_trans,
            'tax_collected_income': self.tax_collected_income,
            'tax_collected_corp': self.tax_collected_corp,
            'tax_total': self.tax_collected_trans + self.tax_collected_income + self.tax_collected_corp,
            'printed_money': self.printed_money,
            'money_spent': self.spent_today,
            'time': self.census_.time
        }


class bank():

    def __init__(self, ID, cash=1000):
        self.ID = ID
        self.census_ = None
        self.cash = cash
        self.loans_in = [] # agent gave money to the bank, the bank pays it back
        self.loans_out = [] # bank gave money to an agent, the agent pays it back
        # resettable variables
        self.loans_taken = 0 # the bank took money, will pay it back
        self.loans_given = 0 # the bank gave money, the agent will pay it back
        self.loans_paid = 0
        self.loans_received = 0

    def reset_day(self):
        self.loans_taken = 0
        self.loans_given = 0
        self.loans_paid = 0
        self.loans_received = 0
    
    def create_loan_offer(self):
        return []
    
    def verify_loan_offer(self, agent, offer):
        # this is a game-play function
        # baseline -> bad
        return True
    
    def take_loan_offer(self, agent, offer):
        gives, amount, period_payment, percent = offer
        line = self.loans_in if gives else self.loans_out
        if gives:
            self.cash += amount
            agent.pay_loan(amount)
            self.loans_taken += amount
        else:
            self.cash -= amount
            agent.receive_loan(amount)
            self.loans_given += amount
        line.append([agent, amount, period_payment, percent])
    
    def run_payment_cycle(self):
        index = 0
        while index < len(self.loans_out):
            agent, amount, period_payment, percent = self.loans_out[index]
            last = (amount <= period_payment)
            cur_payment = min(amount, period_payment)
            success = agent.pay_loan(cur_payment) # should return True if okay, False if nah
            self.cash += cur_payment
            self.loans_received += cur_payment
            self.loans_out[index][1] = (amount - cur_payment) * (1+percent) # update the amount owed to the bank
            if not success or last: # someone went bankrupt :) or it was last payment
                self.loans_out.pop(index)
            index += 1
        index = 0
        while index < len(self.loans_in):
            agent, amount, period_payment, percent = self.loans_in[index]
            last = (amount <= period_payment)
            cur_payment = min(amount, period_payment)
            success = agent.receive_loan(cur_payment) # should return True if okay, False if nah
            self.cash -= cur_payment
            self.loans_paid += cur_payment
            self.loans_in[index][1] = (amount - cur_payment) * (1+percent) # update the amount owed to the bank
            index += 1
    
    def bankrupt(self):
        return (self.cash < 0)

    def make_log(self): # logging
        return {
            'cash': self.cash,
            'loans_taken': self.loans_taken,
            'loans_given': self.loans_given,
            'laons_paid': self.loans_paid,
            'loand_received': self.loans_received,
            'time': self.census_.time
        }


class census(): # meant to easily calculate any metrics for the market (to start with, salary expectation)

    def __init__(self, goods, consumers, producers, banks, g_market, l_market, debt_market, gov):
        self.goods = goods
        self.good_types = {} # private or public goods
        self.consumers = consumers
        self.producers = producers
        self.banks = banks
        self.g_market = g_market
        self.l_market = l_market
        self.debt_market = debt_market
        self.gov = gov
        # here we can store any statistics we wish for other agents to make decisions
        self.stats = {'goods_market_stats': g_market.stats,
                      'loans_market_stats': debt_market.stats,
                      'labor_market_stats': l_market.stats}
        self.time = 0
        # connect census_ to other objects
        for cons_ID, cons in consumers.items():
            cons.census_ = self
            cons.goods = goods
            cons.gov = gov
        for prod_ID, prod in producers.items():
            prod.census_ = self
            prod.goods = goods
            prod.gov = gov
        for bank_ID, bank in banks.items():
            bank.census_ = self
            bank.gov = gov
        g_market.census_ = self
        g_market.goods = goods
        g_market.consumers = consumers
        g_market.producers = producers
        g_market.gov = gov
        l_market.census_ = self
        l_market.consumers = consumers
        l_market.producers = producers
        debt_market.census_ = self
        debt_market.banks = banks
        gov.census_ = self
        gov.goods = goods
        gov.consumers = consumers
        gov.producers = producers
        gov.g_market = g_market
        gov.l_market = l_market
        for good_ID in goods: # it is needed to correctly start the simulation (look start_simulation)
            g_market.trans_today[good_ID] = []
            if goods[good_ID].type:
                for cons_ID, cons in consumers.items():
                    cons.stored_goods[good_ID] = 0
            else:
                gov.stored_public_goods[good_ID] = 0
            for prod_ID, prod in producers.items():
                prod.stored_goods[good_ID] = 0

    def __str__(self):
        return '-' * 10 + '\nCensus print out:\n' + '\n'.join([key + ':\n' + str(val) 
                                                               for key, val in self.stats.items()]) + '\nTime: ' + str(self.time) + '\n' + '-' * 10
    
    def reset_day(self, time):
        self.time = time
        self.file.write('DAY ' + str(time) + ' STARTED\n')
    
    def reflect_day(self):
        pass


class simulation():

    def __init__(self, census_):
        self.consumers = census_.consumers
        self.producers = census_.producers
        self.banks = census_.banks
        self.goods = census_.goods
        self.l_market = census_.l_market
        self.g_market = census_.g_market
        self.debt_market = census_.debt_market
        self.gov = census_.gov
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
        self.l_market.fake_data()
        self.debt_market.fake_data()
        # creating dataframes for logging
        self.df_gmarket = pd.DataFrame(columns=list(self.g_market.make_log()[0].keys()))
        self.df_lmarket = pd.DataFrame(columns=list(self.l_market.make_log().keys()))
        self.df_debt_market = pd.DataFrame(columns=list(self.debt_market.make_log().keys()))
        self.df_cons = pd.DataFrame(columns=list(bob.make_log().keys()))
        self.df_prod = pd.DataFrame(columns=list(tesla.make_log().keys()))
        self.df_banks = pd.DataFrame(columns=list(self.banks[0].make_log().keys()))
        self.df_gov = pd.DataFrame(columns=list(self.gov.make_log().keys()))
        # create a file for the redundant output
        self.census_.file = open('output.txt', 'w')

    def finish_simulation(self): # wrapping up the simulation and saving results
        self.df_cons.to_csv('consumers.csv', index=False, float_format='%.2f')
        self.df_prod.to_csv('producers.csv', index=False, float_format='%.2f')
        self.df_banks.to_csv('banks.csv', index=False, float_format='%.2f')
        self.df_gmarket.to_csv('goods_market.csv', index=False, float_format='%.2f')
        self.df_lmarket.to_csv('labor_market.csv', index=False, float_format='%.2f')
        self.df_debt_market.to_csv('debt_market.csv', index=False, float_format='%.2f')
        self.df_gov.to_csv('government.csv', index=False, float_format='%.2f')
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
        # step six - pay and take loans
        self.pay_take_loans()
        # step seven - goods consumption and depreciation
        self.consume_depreciate()
        # step eight - reflect on the current day
        self.reflect_day()
        # step nine - bankruptcy (and registration of new companies -> later)
        self.bankruptcy()
        # step ten - save logging
        self.logging()
    
    def reset_day(self, time): # step one
        for cons_ID, cons in self.consumers.items():
                cons.reset_day()
        for prod_ID, prod in self.producers.items():
            prod.reset_day()
        self.l_market.reset_day()
        self.g_market.reset_day()
        self.debt_market.reset_day()
        self.gov.reset_day()
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
        for prod_ID, prod in self.producers.items():
            prod.pay_taxes()
    
    def trade_labor(self): # step four
        for prod_ID, prod in self.producers.items(): # producers go first so that fired consumers would have a chance to find a new job
            prod.fire_employee(prod.fire_strategy())
            for skill, salary in prod.hire_strategy():
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
    
    def pay_take_loans(self):  # step six
        for bank_ID, bank in self.banks.items():
            bank.run_payment_cycle()
        for cons_ID, cons in self.consumers.items():
            self.debt_market.add_offer_loan(cons, cons.create_loan_offer())
        for prod_ID, prod in self.producers.items():
            self.debt_market.add_offer_loan(prod, prod.create_loan_offer())
        for bank_ID, bank in self.banks.items():
            self.debt_market.add_offer_loan(bank, bank.create_loan_offer())
        self.debt_market.add_offer_loan(self.gov, self.gov.create_loan_offer())
        self.debt_market.run_day()
        
    def consume_depreciate(self): # step seven
        for cons_ID, cons in self.consumers.items():
            cons.consume_goods()
            cons.depreciate_goods()
        for prod_ID, prod in self.producers.items():
            prod.depreciate_goods()
        self.gov.consume_goods()
        self.gov.depreciate_goods()
        
    def reflect_day(self): # step eight
        self.census_.reflect_day() # should go first
        self.g_market.reflect_day()
        self.l_market.reflect_day()
        self.debt_market.reflect_day()
        self.gov.reflect_day()
        for cons_ID, cons in self.consumers.items():
            cons.reflect_day()
        for prod_ID, prod in self.producers.items():
            prod.reflect_day()

    def bankruptcy(self): # step nine -> to add liquidation of the company later
        for prod_ID, prod in list(self.producers.items()):
            if prod.bankrupt():
                self.producers.pop(prod_ID)
        for bank_ID, bank in list(self.banks.items()):
            if bank.bankrupt():
                self.banks.pop(bank_ID)

    def logging(self): # step ten
        self.df_gmarket = pd.concat([self.df_gmarket, pd.DataFrame(self.g_market.make_log())])
        self.df_lmarket = pd.concat([self.df_lmarket, pd.DataFrame.from_dict(self.l_market.make_log(), orient='index').T])
        self.df_debt_market = pd.concat([self.df_debt_market, pd.DataFrame.from_dict(self.debt_market.make_log(), orient='index').T])
        self.df_gov = pd.concat([self.df_gov, pd.DataFrame.from_dict(self.gov.make_log(), orient='index').T])
        for cons_ID, cons in self.consumers.items():
            self.df_cons = pd.concat([self.df_cons, pd.DataFrame.from_dict(cons.make_log(), orient='index').T])
        for prod_ID, prod in self.producers.items():
            self.df_prod = pd.concat([self.df_prod, pd.DataFrame.from_dict(prod.make_log(), orient='index').T])
        for bank_ID, bank in self.banks.items():
            self.df_banks = pd.concat([self.df_banks, pd.DataFrame.from_dict(bank.make_log(), orient='index').T])
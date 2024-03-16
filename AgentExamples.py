from Agents import good, consumer, producer, bank, goods_market, labor_market, loans_market, government, census, simulation

from random import random as r, randint

def good_consumable(ID_name, is_private): # depreciates slowly, eveything is consumed at once
    return good(ID_name, 0.05, 1.0, is_private)

def good_permanent(ID_name, is_private): # does not depreciate, does not get consumed. Just a static good
    return good(ID_name, 0.0, 0.0, is_private)

def consumer_linear_utility(ID, preference, goods): # preference is a dict {good_ID: utility coef}
    return consumer(ID, lambda x: sum([preference[good_ID] * x[good_ID] if goods[good_ID].type else 0 for good_ID in preference]), 
                    lambda x: sum([preference[good_ID] * x[good_ID] if not goods[good_ID].type else 0 for good_ID in preference]),
                    1000 + r() * 500, 1 + r() * 9)

def consumer_sqrt_utility(ID, preference, goods): # quadratic utility
    return consumer(ID, lambda x: sum([preference[good_ID] * (x[good_ID]**0.5) if goods[good_ID].type else 0 for good_ID in preference]), 
                    lambda x: sum([preference[good_ID] * (x[good_ID]**0.5) if not goods[good_ID].type else 0  for good_ID in preference]),
                    1000 + r() * 500, 1 + r() * 9)

def consumer_mixed_utility(ID, preference, goods): # preference is a dict{good_ID: (utility coef, depend_coef)}
    def depend(num, good_ID): # user can easily add any other preference function here
        pref_type = preference[good_ID][1]
        if pref_type == 'lin':
            return num
        if pref_type == 'sqrt':
            return num ** 0.5
        if pref_type == 'quad':
            return num ** 2
    return consumer(ID, lambda x: sum([preference[good_ID][0] * depend(x[good_ID], good_ID) if goods[good_ID].type else 0 for good_ID in preference]), 
                    lambda x: sum([preference[good_ID][0] * depend(x[good_ID], good_ID) if not goods[good_ID].type else 0 for good_ID in preference]),
                    1000 + r() * 500, 1 + r() * 9)

def producer_sqrt_productivity(ID, good_ID, prod_coef, components, owner):
    return producer(ID, 5000 + 1000 * r(), good_ID, lambda x: prod_coef * x**0.5, components, owner, 100)

def government_flat_taxation(corp_rate, income_rate, trans_rate, budget):
    return government(
        lambda x: x * corp_rate,
        lambda x: x * income_rate,
        {key: (lambda x: x * val) for key, val in trans_rate.items()},
        budget
    )

def sim_set_up(goods_list, cons_list, prod_list, gov, rounds): # this function constructs all the agents and starts the simulation

    # goods_list: [(good_type, good_name)]
    # cons_list: [(num, cons_type, cons_pref)]
    # prod_list: [(num, prod_type, prod_good_ID, prod_coef, prod_comp, prod_owner)]
    # rounds: int (this is number of rounds in the simulation)

    # later we might change the structure to [(num, type, {<all the necessary info>})]

    goods = {}
    for good_type, good_name, is_private in goods_list:
        goods[good_name] = good_type(good_name, is_private)

    consumers = {}

    ID = 0
    for num, cons_type, cons_pref in cons_list:
        for i in range(num):
            consumers[ID] = cons_type(ID, cons_pref, goods)
            ID += 1
    tot_consumers = ID

    producers = {}

    ID = 0
    for num, prod_type, prod_good_ID, prod_coef, prod_comp, prod_owner in prod_list:
        for i in range(num):
            owner = consumers[randint(0, tot_consumers-1) if prod_owner == None else prod_owner]
            producers[ID] = prod_type(ID, prod_good_ID, prod_coef, prod_comp, owner)
            ID += 1
    tot_producers = ID

    banks = {}
    for ID in range(5):
        banks[ID] = bank(ID)

    goods_market_ = goods_market()
    labor_market_ = labor_market()
    debt_market = loans_market()

    # census argument: goods, consumers, producers, banks, g_market, l_market, debt_market, gov
    census_ = census(goods, consumers, producers, banks, goods_market_, labor_market_, debt_market, gov)

    sim = simulation(census_)
    sim.run(rounds)

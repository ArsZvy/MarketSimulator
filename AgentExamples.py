from Agents import good, consumer, producer, goods_market, labor_market, census, simulation

from random import random as r, randint

def good_consumable(ID_name): # depreciates slowly, eveything is consumed at once
    return good(ID_name, 0.05, 1.0)

def good_permanent(ID_name): # does not depreciate, does not get consumed. Just a static good
    return good(ID_name, 0.0, 0.0)

def consumer_linear_utility(ID, preference): # preference is a dict {good_ID: utility coef}
    return consumer(ID, lambda x: sum([preference[good_ID] * x[good_ID] for good_ID in preference]), 1000 + r() * 500, 1 + r() * 9)

def consumer_sqrt_utility(ID, preference): # quadratic utility
    return consumer(ID, lambda x: sum([preference[good_ID] * (x[good_ID]**0.5) for good_ID in preference]), 1000 + r() * 500, 1 + r() * 9)

def consumer_mixed_utility(ID, preference): # preference is a dict{good_ID: (utility coef, depend_coef)}
    def depend(num, good_ID): # user can easily add any other preference function here
        pref_type = preference[good_ID][1]
        if pref_type == 'lin':
            return num
        if pref_type == 'sqrt':
            return num ** 0.5
        if pref_type == 'quad':
            return num ** 2
    return consumer(ID, lambda x: sum([preference[good_ID][0] * depend(x[good_ID], good_ID) for good_ID in preference]), 
                    1000 + r() * 500, 1 + r() * 9)

def producer_sqrt_productivity(ID, good_ID, prod_coef, components, owner):
    return producer(ID, 5000 + 1000 * r(), good_ID, lambda x: prod_coef * x**0.5, components, owner, 100)

def sim_set_up(goods_list, cons_list, prod_list, rounds): # this function constructs all the agents and starts the simulation

    # goods_list: [(good_type, good_name)]
    # cons_list: [(num, cons_type, cons_pref)]
    # prod_list: [(num, prod_type, prod_good_ID, prod_coef, prod_comp, prod_owner)]
    # rounds: int (this is number of rounds in the simulation)

    # later we might change the structure to [(num, type, {<all the necessary info>})]

    goods = {}
    for good_type, good_name in goods_list:
        goods[good_name] = good_type(good_name)

    consumers = {}

    ID = 0
    for num, cons_type, cons_pref in cons_list:
        for i in range(num):
            consumers[ID] = cons_type(ID, cons_pref)
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

    goods_market_ = goods_market()
    labor_market_ = labor_market()
    census_ = census(goods, consumers, producers, goods_market_, labor_market_)

    sim = simulation(consumers, producers, goods, goods_market_, labor_market_, census_)
    sim.run(rounds)

from Agents import good, consumer, producer, goods_market, labor_market, census, simulation
from AgentExamples import *

from random import random as r, randint

def sim_set_up(goods_list, cons_list, prod_list, rounds): # this function constructs all the agents and starts the simulation

    # goods_list: [(good_type, good_name)]
    # cons_list: [(num, cons_type, cons_pref)]
    # prod_list: [num, prod_type, prod_good_ID, prod_coef, prod_comp, prod_owner]
    # rounds: int (this is number of rounds in the simulation)

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

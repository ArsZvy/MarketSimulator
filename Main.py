from Agents import good, consumer, producer, goods_market, labor_market, census, simulation

from random import random as r

def create_agents(): # this function creates consumers, producers, goods, markets and so on. Return tuple (consumers, producers, goods, g_market, l_market, census_)
    # THIS function should be adjusted for different simulations

    # CURRENT SIMULATION SET UP
    # There are only three goods in the world: apples, pears, and art
    # Apples and pears are completely consumed each round, whereas a piece of art is permenant
    # There are two groups of people: people who do not love art, and people who enjoy art
    # Their utility of apples and pears are similar
    # However the utility of art for the first group is zero, whereas for the second one it is a scaled square root function
    # The typical change in utility is:
    # You consume one apple / pear -> increase by 1 util
    # You consume one piece of art -> increase by 3 utils, then by 1.5 utils, then by 1.0 util and so on (diminishing value)
    # There are ten companies producing each good, so we get a sustainable market
    # Productivity function of apple / pear companies increase like this:
    # 0 people -> 4.5 apples, 1 people -> 11 apples, 2 people -> 15.5 apples and so on (diminishing value of labor)
    # For art companies (also, one apple needed to produce each art):
    # 0 people -> 7.5 arts, 1 people -> 18.5 arts, 2 people -> 26 arts

    # initialize consumers, producers, and goods
    # apples and pears are completely consumed every round and slightly rot, whereas art stays permanent
    goods = {'apple' : good('apple', lambda x: x*0.95, lambda x: (x, 0)), 
             'art' : good('art', lambda x: x, lambda x: (x, x)), 
             'pear': good('pear', lambda x: x*0.9, lambda x: (x, 0))}

    consumers = {}

    for i in range(50): # people who do not love art
        ID = i
        coef1, coef2, coef3 = 1 + 0.1*r(), 0, 1 + 0.1*r()
        bob = consumer(ID, lambda x: x['apple']*coef1 + (x['art']**0.5)*coef2 + x['pear']*coef3, 1000 + r() * 500, 1 + r() * 9, goods)
        consumers[ID] = bob
    for i in range(50): # people who love art
        ID = i+50
        coef1, coef2, coef3 = 1 + 0.1*r(), 3 + 0.1 * r(), 1 + 0.1*r()
        bob = consumer(ID, lambda x: x['apple']*coef1 + (x['art']**0.5)*coef2 + x['pear']*coef3, 1000 + r() * 500, 1 + r() * 9, goods)
        consumers[ID] = bob

    producers = {}

    for i in range(10):
        # apple producing companies
        coef = r()
        ID = i
        owner = consumers[int(r() * 60)]
        tesla = producer(ID, 5000 + 1000 * r(), 'apple', lambda x: (4 + coef) * x**0.5, {}, owner, 10, goods)
        producers[ID] = tesla
    for i in range(10):
        # art producing companies need less labor to produce a unit, BUT they have a needed input: one apple
        coef = r()
        ID = i + 10
        owner = consumers[int(r() * 60)]
        tesla = producer(ID, 5000 + 1000 * r(), 'art', lambda x: (7 + coef) * x**0.5, {'apple': 1.0}, owner, 10, goods)
        producers[ID] = tesla
    for i in range(10):
        # pear producing companies
        coef = r()
        ID = i + 20
        owner = consumers[int(r() * 60)]
        tesla = producer(ID, 5000 + 1000 * r(), 'pear', lambda x: (4 + coef) * x**0.5, {}, owner, 10, goods)
        producers[ID] = tesla

    # you typically do not want to change these lines
    goods_market_ = goods_market(goods, consumers, producers)
    labor_market_ = labor_market(consumers, producers)
    census_ = census(goods, consumers, producers, goods_market_, labor_market_)

    return (consumers, producers, goods, goods_market_, labor_market_, census_)

if __name__ == '__main__':
    consumers, producers, goods, goods_market_, labor_market_, census_ = create_agents()
    sim = simulation(consumers, producers, goods, goods_market_, labor_market_, census_)
    sim.run(100)
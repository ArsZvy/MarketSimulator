from Agents import good, consumer, producer, goods_market, labor_market, census, simulation

from random import random as r

def create_agents(): # this function creates consumers, producers, goods, markets and so on. Return tuple (consumers, producers, goods, g_market, l_market, census_)
    # THIS function should be adjusted for different simulations

    # CURRENT SIMULATION SET UP
    # There are only two goods in the world: apples and art
    # Apples are completely consumed each round, whereas a piece of art is permenant (look at depreciation functions)
    # There are two groups of people: people who do not love art, and people who enjoy art
    # Their utility of apples is similar, however the utility of art for the first group is zero, whereas for the second one it is a scaled square root function
    # The typical change in utility is:
    # You consume one apple -> increase by 1 util
    # You buy one piece of art -> increase by 2.5 utils, then by 1.5 utils, then by 1.0 util and so on (diminishing value)
    # There are two apple producing compnaies and two art producing ones
    # Productivity function of apple companies increase like this:
    # 0 people -> 4.5 apples, 1 people -> 11 apples, 2 people -> 15.5 apples and so on (diminishing value of labor)
    # For art companies (also, one apple needed to produce each art):
    # 0 people -> 7.5 arts, 1 people -> 18.5 arts, 2 people -> 26 arts

    # THE HYPOTHESIS OF THE SIMULATION
    # The price of apple would stabilize around some value
    # The price of art would initially rise and stay high for a couple of rounds and then would drop almost to zero 
    # (as people would get saturated with art as it does not depreciate)
    # Consumers would initially buy both apples (everyone) and art (the art-lovers), 
    # but then they would stop buying art at all (saturation) and would switch to apples completely
    # Initially, people would be employed by both apple and art producers
    # Later, art producers would fire everyone, and apple producers would accumulate all the labor work force
    # The income of all the companies would fall to almost zero, so the revenue from sales would equate the salaries
    # From some math derivations, the equilibrium would be:
    # 60 apples produced, 0 arts produced per round
    # about 3000 in a round circulation
    # apple price is about 50, average salary for each skill point is 50

    # AFTER THESE PREDICTIONS ARE ACHIEVED AND VERIFIED, THE TESTING OF THE DEMO SIMULATION IS DONE!

    # initialize consumers, producers, and goods
    goods = {'apple' : good('apple', lambda x: x*0.5), 'art' : good('art', lambda x: x)}

    consumers = {}

    for i in range(5): # people who do not love art
        ID = i
        coef1, coef2 = 0.9 + 0.2*r(), 0
        bob = consumer(ID, lambda x: x['apple'] * coef1 + (x['art']**0.5) * coef2, r() * 1000, 1 + r() * 9, goods)
        consumers[ID] = bob
    for i in range(5): # people who love art
        ID = i+5
        coef1, coef2 = 0.9 + 0.2*r(), 4 + 0.1 * r()
        bob = consumer(ID, lambda x: x['apple'] * coef1 + (x['art']**0.5) * coef2, r() * 1000, 1 + r() * 9, goods)
        consumers[ID] = bob

    producers = {}

    for i in range(2):
        coef = r()
        # apple producing companies
        tesla = producer(i, 10000 * r(), 'apple', 0.0, lambda x: (4 + coef) * x**0.5, {}, bob, 10, goods) # made last consumer to be the owner of all companies
        producers[i] = tesla
    for i in range(2):
        coef = r()
        # art producing companies need less labor to produce a unit, BUT they have a needed input: one apple
        tesla = producer(2+i, 10000 * r(), 'art', 0.0, lambda x: (7 + coef) * x**0.5, {'apple': 1.0}, bob, 10, goods)
        producers[2+i] = tesla

    # you typically do not want to change these lines
    goods_market_ = goods_market(goods, consumers, producers)
    labor_market_ = labor_market(consumers, producers)
    census_ = census(goods, consumers, producers, goods_market_, labor_market_)

    return (consumers, producers, goods, goods_market_, labor_market_, census_)

if __name__ == '__main__':
    consumers, producers, goods, goods_market_, labor_market_, census_ = create_agents()
    sim = simulation(consumers, producers, goods, goods_market_, labor_market_, census_)
    sim.run(50)


# TO DO
# DEBUG THE DEMO!
# Maybe move depreciation to the last phase?
# Maybe add one more phase of "reflection"?
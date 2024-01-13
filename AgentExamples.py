from Agents import good, consumer, producer, goods_market, labor_market, census, simulation

from random import random as r

def good_consumable(ID_name): # depreciates slowly, eveything is consumed at once
    return good(ID_name, 0.05, 1.0)

def good_permanent(ID_name): # does not depreciate, does not get consumed. Just a static good
    return good(ID_name, 0.0, 0.0)

def consumer_linear_utility(ID, preference): # preference is a dict {good_ID: utility coef}
    return consumer(ID, lambda x: sum([preference[good_ID] * x[good_ID] for good_ID in preference]), 1000 + r() * 500, 1 + r() * 9)

def consumer_quad_utility(ID, preference): # quadratic utility
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

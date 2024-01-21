from AgentExamples import *

def sim_set_up_1():

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

    sim_set_up(
        [(good_consumable, 'apple'),
        (good_permanent, 'art'),
        (good_consumable, 'pear')],

        [(50, consumer_linear_utility, {'apple': 1, 'pear': 1}),
        (50, consumer_mixed_utility, {'apple': (1, 'lin'), 'pear': (1, 'lin'), 'art': (3, 'sqrt')})],


        [(10, producer_sqrt_productivity, 'apple', 7, {}, None),
        (10, producer_sqrt_productivity, 'art', 4, {'apple': 1.0}, None),
        (10, producer_sqrt_productivity, 'pear', 7, {}, None)],

        30
    )

def sim_set_up_2():

    # here 'art' is addictive: the more you have it, the more you want it
    # We should expect the market to pivot towards art production

    sim_set_up(
        [(good_consumable, 'apple'),
         (good_consumable, 'art')],

        [(100, consumer_mixed_utility, {'apple': (1, 'lin'), 'art': (1.0, 'quad')})],

        [(10, producer_sqrt_productivity, 'apple', 10, {}, None),
          (10, producer_sqrt_productivity, 'art', 10, {}, None)],

        30
    )

def sim_set_up_3():

    # we have only one company producing each good -> expect huge profits and poor population

    sim_set_up(
        [(good_consumable, 'apple'),
         (good_permanent, 'art')],

        [(100, consumer_linear_utility, {'apple': 1, 'art': 1})],

        [(1, producer_sqrt_productivity, 'apple', 5, {}, None),
         (1, producer_sqrt_productivity, 'art', 5, {}, None)],

        50
    )

def sim_set_up_4(): # takes about 2 mins on my local machine

    # stress testing: huge volumes

    sim_set_up(
        [(good_consumable, 'apple'),
         (good_consumable, 'pear'),
         (good_consumable, 'bread'),
         (good_permanent, 'art'),
         (good_permanent, 'car')],

        [(250, consumer_mixed_utility, {'apple': (1, 'lin'), 'pear': (3, 'quad'), 'bread': (2, 'sqrt'), 'art': (1, 'lin')}),
         (250, consumer_mixed_utility, {'apple': (4, 'quad'), 'pear': (2, 'lin'), 'bread': (3, 'lin'), 'art': (4, 'lin')}),
         (200, consumer_mixed_utility, {'apple': (2, 'sqrt'), 'pear': (5, 'lin'), 'bread': (1, 'quad')})], # check if dict is not full

        [(30, producer_sqrt_productivity, 'apple', 3, {}, None),
         (20, producer_sqrt_productivity, 'pear', 2, {'apple': 1}, None),
         (15, producer_sqrt_productivity, 'bread', 4, {}, None),
         (20, producer_sqrt_productivity, 'art', 5, {'apple': 1, 'pear': 2}, None),
         (5, producer_sqrt_productivity, 'car', 4, {}, None)],

        100
    )

def sim_set_up_5():

    # simplest case -> one good only, many companies. Expect stable economical system

    sim_set_up(
        [(good_consumable, 'apple')],

        [(100, consumer_linear_utility, {'apple': 3})],

        [(10, producer_sqrt_productivity, 'apple', 3, {}, None)],

        50
    )



# goods_list: [(good_type, good_name)]
# cons_list: [(num, cons_type, cons_pref)]
# prod_list: [num, prod_type, prod_good_ID, prod_coef, prod_comp, prod_owner]
# rounds: int (this is number of rounds in the simulation)

if __name__ == '__main__':
    sim_set_up_1() # choose the simulation to run here

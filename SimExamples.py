from AgentExamples import *
from SimSetUp import sim_set_up

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

        [(50, consumer_linear_utility, {'apple': 1+0.1*r(), 'pear': 1+0.1*r()}),
        (50, consumer_mixed_utility, {'apple': (1+0.1*r(), 'lin'), 'pear': (1+0.1*r(), 'lin'), 'art': (3+0.1*r(), 'sqrt')})],


        [(10, producer_sqrt_productivity, 'apple', 7, {}, None),
        (10, producer_sqrt_productivity, 'art', 4, {'apple': 1.0}, None),
        (10, producer_sqrt_productivity, 'pear', 7, {}, None)],

        30
    )

if __name__ == '__main__':
    sim_set_up_1() # choose the simulation to run here

from Visuals import *

def visual_set_up_1():
    visual_set_up([
        (plot_good_price, 'apple'),
        (plot_good_price, 'art'),
        (plot_good_items_sold, 'apple'),
        (plot_good_items_sold, 'art'),
        (plot_employment_rate, None),
        (plot_mean_salary, None),
        (plot_mean_utility, None),
        (plot_tot_market_cap, None),
        (plot_good_market_cap, 'apple')
    ])

if __name__ == '__main__':
    visual_set_up_1()
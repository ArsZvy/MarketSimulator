from Visuals import Visual as vs

def visual_set_up_1(): # focus on the goods market
    vs([
        (vs.plot_good_price, 'apple'),
        (vs.plot_good_price, 'art'),
        (vs.plot_tot_market_cap, None),
        (vs.plot_good_market_cap, 'apple'),
        (vs.plot_good_items_sold, 'apple'),
        (vs.plot_good_items_offered, 'apple'),
        (vs.plot_good_market_cap, 'art'),
        (vs.plot_good_items_sold, 'art'),
        (vs.plot_good_items_offered, 'art')
    ])

def visual_set_up_2():
    vs([
        (vs.plot_mean_utility, None),
        (vs.plot_mean_salary, None),
        (vs.plot_employment_rate, None),
        (vs.plot_number_hired, None),
        (vs.plot_share_hired, None),
        (vs.plot_hired_salary_skill_ratio, None),
        (vs.plot_mean_income, 'apple'),
        (vs.plot_price_expectation, 'apple'),
        (vs.plot_good_price, 'apple')
    ])

if __name__ == '__main__':
    visual_set_up_2()

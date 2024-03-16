import pandas as pd
import matplotlib.pyplot as plt

class Visual():

    def __init__(self, temp):
        df_gmarket = pd.read_csv('goods_market.csv')
        df_lmarket = pd.read_csv('labor_market.csv')
        df_cons = pd.read_csv('consumers.csv')
        df_prod = pd.read_csv('producers.csv')
        # give the simulation five rounds to adapt
        self.df_gm = df_gmarket[df_gmarket['time'] > 5]
        self.df_lm = df_lmarket[df_lmarket['time'] > 5]
        self.df_cons = df_cons[df_cons['time'] > 5]
        self.df_prod = df_prod[df_prod['time'] > 5]
        # Creating subplots
        plt.figure(figsize=(10, 6))  # Adjust the figure size if needed

        pos = 1
        eps = 0.001
        dim_size = int(len(temp) ** 0.5 + 1 - eps)
        for func, arg in temp:
            plt.subplot(dim_size, dim_size, pos)
            func(self, arg)
            pos += 1

        plt.tight_layout()  # Adjusts subplot parameters for better layout
        plt.show()

    # GOODS MARKET STATS

    def plot_good_price(self, good_ID):
        plt.plot(self.df_gm[self.df_gm['good_ID'] == good_ID]['time'], self.df_gm[self.df_gm['good_ID'] == good_ID]['avg_price_wtax'])
        plt.title(good_ID + ' price')

    def plot_tot_market_cap(self, arg=None):
        cap_by_good = pd.DataFrame(self.df_gm['time'], columns=['time'])
        cap_by_good['cap'] = self.df_gm['avg_price_wtax'] * self.df_gm['items_sold']
        tot_cap = cap_by_good.groupby(by='time').sum().reset_index()
        plt.plot(tot_cap['time'], tot_cap['cap'])
        plt.title('Total market cap')

    def plot_good_market_cap(self, good_ID):
        good_df = self.df_gm[self.df_gm['good_ID'] == good_ID]
        plt.plot(good_df['time'], good_df['items_sold'] * good_df['avg_price_wtax'])
        plt.title(good_ID + ' market cap')

    def plot_good_items_sold(self, good_ID):
        plt.plot(self.df_gm[self.df_gm['good_ID'] == good_ID]['time'], self.df_gm[self.df_gm['good_ID'] == good_ID]['items_sold'])
        plt.title(good_ID + ' sold')
    
    def plot_good_items_offered(self, good_ID):
        plt.plot(self.df_gm[self.df_gm['good_ID'] == good_ID]['time'], self.df_gm[self.df_gm['good_ID'] == good_ID]['items_offered'])
        plt.title(good_ID + ' offered')
    
    def plot_good_items_sold_share(self, good_ID):
        df_good = self.df_gm[self.df_gm['good_ID'] == good_ID]
        plt.plot(df_good['time'], (df_good['items_sold']+1) / (df_good['items_offered']+1))
        plt.title(good_ID + ' share sold')

    # LABOR MARKET STATS
    
    def plot_number_hired(self, arg=None):
        plt.plot(self.df_lm['time'], self.df_lm['hired'])
        plt.title('Number Hired')
    
    def plot_share_hired(self, arg=None):
        plt.plot(self.df_lm['time'], self.df_lm['hired'] / self.df_lm['candidates'])
        plt.title('Share Hired')
    
    def plot_hired_salary_skill_ratio(self, arg=None):
        plt.plot(self.df_lm['time'], self.df_lm['avg_hired_salary'] / self.df_lm['avg_hired_skill'])
        plt.title('Current salary to skill ratio')

    # CONSUMERS STATS

    def plot_mean_utility(self, arg=None):
        by_util = self.df_cons.groupby('time')['utility'].mean().reset_index()
        plt.plot(by_util['time'], by_util['utility'])
        plt.title('Average utility')

    def plot_mean_salary(self, arg=None):
        by_sal = self.df_cons.groupby('time')['salary'].mean().reset_index()
        plt.plot(by_sal['time'], by_sal['salary'])
        plt.title('Average salary')

    def plot_employment_rate(self, arg=None):
        cur_df = self.df_cons[['time']].copy()
        cur_df['emp'] = self.df_cons['salary'] > 0
        by_emp = cur_df.groupby('time')['emp'].mean().reset_index()
        plt.plot(by_emp['time'], by_emp['emp'])
        plt.title('Employment rate')

    # PRODUCERS STATS
    
    def plot_price_expectation(self, good_ID):
        good_df = self.df_prod[self.df_prod['good ID'] == good_ID]
        price_exp = good_df.groupby('time')['price exp'].mean().reset_index()
        plt.plot(price_exp['time'], price_exp['price exp'])
        plt.title(good_ID + ' price expectation')
    
    def plot_mean_income(self, good_ID):
        good_df = self.df_prod[self.df_prod['good ID'] == good_ID]
        income = good_df.groupby('time')['income'].mean().reset_index()
        plt.plot(income['time'], income['income'])
        plt.title(good_ID + ' mean income')

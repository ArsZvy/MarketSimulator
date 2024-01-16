import pandas as pd
import matplotlib.pyplot as plt

def plot_good_price(pos, df, df_cons, df_prod, good_ID):
    plt.subplot(3, 3, pos)
    plt.plot(df[df['good ID'] == good_ID]['time'], df[df['good ID'] == good_ID]['avg price'])
    plt.title(good_ID + ' price')

def plot_tot_market_cap(pos, df, df_cons, df_prod, arg=None):
    plt.subplot(3, 3, pos)
    cap_by_good = pd.DataFrame(df['time'], columns=['time'])
    cap_by_good['cap'] = df['avg price'] * df['items sold']
    tot_cap = cap_by_good.groupby(by='time').sum().reset_index()
    plt.plot(tot_cap['time'], tot_cap['cap'])
    plt.title('Total market cap')

def plot_good_market_cap(pos, df, df_cons, df_prod, good_ID):
    plt.subplot(3, 3, pos)
    good_df = df[df['good ID'] == good_ID]
    plt.plot(good_df['time'], good_df['items sold'] * good_df['avg price'])
    plt.title(good_ID + ' market cap')

def plot_good_items_sold(pos, df, df_cons, df_prod, good_ID):
    plt.subplot(3, 3, pos)
    plt.plot(df[df['good ID'] == good_ID]['time'], df[df['good ID'] == good_ID]['items sold'])
    plt.title(good_ID + ' sold')

def plot_mean_utility(pos, df, df_cons, df_prod, arg=None):
    by_util = df_cons.groupby('time')['utility'].mean().reset_index()
    plt.subplot(3, 3, pos)
    plt.plot(by_util['time'], by_util['utility'])
    plt.title('Average utility')

def plot_mean_salary(pos, df, df_cons, df_prod, arg=None):
    by_sal = df_cons.groupby('time')['salary'].mean().reset_index()
    plt.subplot(3, 3, pos)
    plt.plot(by_sal['time'], by_sal['salary'])
    plt.title('Average salary')

def plot_employment_rate(pos, df, df_cons, df_prod, arg=None):
    df_cons['emp'] = df_cons['salary'] > 0
    by_emp = df_cons.groupby('time')['emp'].mean().reset_index()
    plt.subplot(3, 3, pos)
    plt.plot(by_emp['time'], by_emp['emp'])
    plt.title('Employment rate')

def visual_set_up(temp):
    df = pd.read_csv('goods_market.csv')
    df_cons = pd.read_csv('consumers.csv')
    df_prod = pd.read_csv('producers.csv')
    # give the simulation five rounds to adapt
    df = df[df['time'] > 5]
    df_cons = df_cons[df_cons['time'] > 5]
    df_prod = df_prod[df_prod['time'] > 5]
    # Creating subplots
    plt.figure(figsize=(10, 6))  # Adjust the figure size if needed

    pos = 1
    for func, arg in temp:
        func(pos, df, df_cons, df_prod, arg)
        pos += 1

    plt.tight_layout()  # Adjusts subplot parameters for better layout
    plt.show()
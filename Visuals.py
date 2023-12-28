import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('goods_market.csv')
df_cons = pd.read_csv('consumers.csv')
df_prod = pd.read_csv('producers.csv')
# give the simulation five rounds to adapt
df = df[df['time'] > 5]
df_cons = df_cons[df_cons['time'] > 5]
df_prod = df_prod[df_prod['time'] > 5]

# Creating subplots
plt.figure(figsize=(10, 4))  # Adjust the figure size if needed

plt.subplot(3, 3, 1)
plt.plot(df[df['good ID'] == 'apple']['time'], df[df['good ID'] == 'apple']['avg price'])
plt.title('Apple price')

plt.subplot(3, 3, 2)
apple_cap = df[df['good ID'] == 'apple']['avg price'] * df[df['good ID'] == 'apple']['items sold']
pear_cap = df[df['good ID'] == 'pear']['avg price'] * df[df['good ID'] == 'pear']['items sold']
art_cap = df[df['good ID'] == 'art']['avg price'] * df[df['good ID'] == 'art']['items sold']
plt.plot(df[df['good ID'] == 'apple']['time'], apple_cap.values + pear_cap.values + art_cap.values)
plt.title('Total market cap')

plt.subplot(3, 3, 4)
plt.plot(df[df['good ID'] == 'art']['time'], df[df['good ID'] == 'art']['avg price'])
plt.title('Art price')

plt.subplot(3, 3, 5)
plt.plot(df[df['good ID'] == 'art']['time'], df[df['good ID'] == 'art']['avg price'] * df[df['good ID'] == 'art']['items sold'])
plt.title('Art market cap')

plt.subplot(3, 3, 3)
plt.plot(df[df['good ID'] == 'apple']['time'], df[df['good ID'] == 'apple']['items sold'])
plt.title('Apples sold')

plt.subplot(3, 3, 6)
plt.plot(df[df['good ID'] == 'art']['time'], df[df['good ID'] == 'art']['items sold'])
plt.title('Art sold')

by_util = df_cons.groupby('time')['utility'].mean().reset_index()

plt.subplot(3, 3, 7)
plt.plot(by_util['time'], by_util['utility'])
plt.title('Average utility')

by_sal = df_cons.groupby('time')['salary'].mean().reset_index()

plt.subplot(3, 3, 8)
plt.plot(by_sal['time'], by_sal['salary'])
plt.title('Average salary')

df_cons['emp'] = df_cons['salary'] > 0
by_emp = df_cons.groupby('time')['emp'].mean().reset_index()

plt.subplot(3, 3, 9)
plt.plot(by_emp['time'], by_emp['emp'])
plt.title('Employment rate')

plt.tight_layout()  # Adjusts subplot parameters for better layout
plt.show()

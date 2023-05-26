from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_sql("SELECT * FROM evs_per_capita", 'sqlite:///data/clean/evs_per_capita.sqlite')
df['electric_and_hybrid_total'] = df['electric_total'] + df['hybrid_total']

print(df.head())

z = np.polyfit(df['gdp_per_capita'], df['share_electric'], 1)
p = np.poly1d(z)

df.plot.scatter('gdp_per_capita','share_electric', c='total', colormap='viridis')

plt.plot(df['gdp_per_capita'], p(df['gdp_per_capita']))

# df.plot.scatter('gdp_per_capita','electric_total')


plt.show()

from matplotlib import pyplot as plt
import pandas as pd

df = pd.read_sql("SELECT * FROM evs_per_capita", 'sqlite:///data/clean/evs_per_capita.sqlite')

print(df.head())

df.plot.scatter('gdp_per_capita','share_electric')
df.plot.scatter('gdp_per_capita','electric_total')


plt.show()

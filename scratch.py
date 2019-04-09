import pandas as pd

path = '/home/david/Downloads/DP_LIVE_01042019144928525.csv'

df = pd.read_csv(open(path))
print(df.head())
print(df['SUBJECT'])

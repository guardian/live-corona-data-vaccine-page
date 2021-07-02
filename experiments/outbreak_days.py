#%%

import pandas as pd 
import os 
import pytz
import datetime
import numpy

today = datetime.datetime.now(pytz.timezone("Australia/Sydney"))
today = datetime.datetime.strftime(today, '%Y-%m-%d')
today = datetime.datetime.strptime(today, '%Y-%m-%d')

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

fillo = f"experiments/breaches.csv"

#%%

df = pd.read_csv(fillo, skiprows=4)
df = df.dropna(subset=['LINK'])
df = df[['NO', 'STATE', 'DATE', 'FACILITY',
       'CASE NAME', 'VARIANT', 'ONWARD', 'VAX', 'LINK']]
df = df.loc[df['STATE'] != "STATE"]

df['DATE'] = pd.to_datetime(df['DATE'])

# print(df)
# print(df.columns)


#%%

## WORK OUT DAYS SINCE LAST BREACH

listo = []

for state in df['STATE'].unique().tolist():
    inter = df.loc[df["STATE"] == state].copy()
    latest = inter.loc[inter['DATE'] == inter['DATE'].max()]

    latest_date = latest['DATE'].values[0]
    latest_date = pd.Timestamp(latest_date).to_pydatetime()

    delta = today - latest_date
    delta = delta.days

    latest['Days since'] = delta

    # print(type(latest_date))

    listo.append(latest)

final = pd.concat(listo)

final = final[["STATE", "Days since"]]
final.columns = ['State', "Days since last quarantine breach"]




#%%

## WORK OUT TOTAL NUMBER OF BREACHES BY STATE


grouped = df.groupby(by="STATE").count().reset_index()
grouped = grouped[['STATE', 'NO']]
grouped.columns = ["State", "Number of breaches"]

### Combine

combo = pd.merge(grouped, final, on="State")

print(combo)
print(combo.columns)



# print(my_date)

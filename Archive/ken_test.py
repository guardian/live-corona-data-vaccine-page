#%%
import pandas as pd
pd.set_option("display.max_columns", 100)

url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

air = pd.read_json(url)

#%%

dair = air.copy()

dair['Second_doses'] = dair['AIR_12_15_SECOND_DOSE_COUNT'] + dair['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT']

dair = dair[['DATE_AS_AT','Second_doses']]
dair['Eligible'] = dair['Second_doses'].shift(90)

booster_eligible = dair['Eligible'].max()

p = dair

print(p.tail(30))
print(p.columns.tolist())

print(p.loc[(p['DATE_AS_AT'] >= "2021-10-05") & (p['DATE_AS_AT'] < "2021-10-20")])

print(booster_eligible)

# %%

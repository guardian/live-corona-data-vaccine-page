#%%

import pandas as pd 
import datetime
from yachtcharter import yachtCharter
chart_key = f"oz-covid-indigenous_vs_non_indigenous_vax_rates"

fillo = 'https://vaccinedata.covid19nearme.com.au/data/all.csv'

#%%

### THESE ARE 12+ POPULATIONS, AS USED IN OUR SPREADSHEET
# https://docs.google.com/spreadsheets/d/1cR0XSzndyV7J4IbNzvnKBK2diuOB6Bo0FUBzztcPlCk/edit#gid=71499319
pops = {"indig":591170, 'non_indig': 21272779}

df = pd.read_csv(fillo)


cols = [x for x in df.columns.tolist() if "FIRST_NATIONS" in x]

p = cols

print(p)
# print(p.columns.tolist())
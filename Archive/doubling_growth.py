#%%

import pandas as pd
import datetime
import numpy as np
import os, ssl
pd.set_option("display.max_rows", None, "display.max_columns", None)

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

oz_json = 'https://covidlive.com.au/covid-live.json'

#%%

oz = pd.read_json(oz_json)
oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
oz = oz.sort_values(by="REPORT_DATE", ascending=True)

oz = oz.loc[oz['NAME'] == "NSW"]

oz = oz[['REPORT_DATE', 'PREV_CASE_CNT']]



# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT',
#        'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
#        'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT',
#        'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT',
#        'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT',
#        'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT',
#        'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT',
#        'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT',
#        'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT',
#        'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT',
#        'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT',
#        'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT',
#        'VACC_GP_CNT', 'PREV_VACC_GP_CNT'



#%%

oz["New"] = oz['PREV_CASE_CNT'].diff(1)

# oz.loc[oz["New"] < 0, "New"] = 0

oz = oz.loc[oz['New'] > 0]

# %%



# latest = oz.loc[oz['REPORT_DATE'] == oz['REPORT_DATE'].max()]['New'].values[0]

# modular = latest % 2

# oz['Double'] = 

# print(latest)

# oz['Diff'] = oz['New'] % latest

# print(oz)
# print(oz.columns)
# %%


oz['New'] = oz['New'].rolling(window=7).mean()

oz = oz.loc[oz['REPORT_DATE'] > "2021-05-01"]

import numpy as np
from scipy.interpolate import interp1d
np.set_printoptions(suppress=True)

y = oz['New'].to_numpy()

# print(y)

x = np.arange(y.shape[0])


dy = np.diff(y)

# these are the places without increase
idx = np.argwhere(dy)

y_fixed = y.copy()

# Hack: increase the second identical value be a
# small amount so the interpolation works
# increase the indices by one to increment the second value
y_fixed[idx + 1] += 0.001

# you need scipy > 0.17 for extrapolation to work
f = interp1d(y_fixed, x, fill_value="extrapolate")

# there are the values you need?
y_half = y / 2.0

# print(y_half)

# get the according x values by interpolation
x_interp = f(y_half)

print(x_interp)

# delta between the current day and the date when
# the value was half
dbl = x - x_interp

# this already looks quite good, but double check!
print(dbl)
# %%

#%%

import pandas as pd 
import requests
import json
# pd.set_option("display.max_rows", 100)
# from yachtcharter import yachtCharter
# chart_key = f"oz-datablogs-something_random{igloo}"

fillo = 'https://raw.githubusercontent.com/hodcroftlab/covariants/master/web/data/perCountryData.json'

#%%

r = requests.get(fillo)


#%%
data = json.loads(r.text)

# df = pd.DataFrame()

for i in data['regions'][0]['distributions']:
    if i['country'] == 'Australia':
        df = pd.json_normalize(i['distribution'])

        print(df)
        print(df.columns)
        


        with open('oz.csv', 'w') as f:
            df.to_csv(f, index=False, header=True)
        # print(df)
        # print(df.columns)

        # print(i['distribution'])
    # print(i['country'])

# print(data['regions'])
# print(data.keys())
# df = pd.read_json(data)
# df = pd.DataFrame.from_dict(data)

# p = df

# # vchecker = 'gdp_per_capita'
# # print(p.loc[p[vchecker].isna()])
# print(p)
# print(p.columns.tolist())
# %%


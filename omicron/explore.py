#%%

import pandas as pd 
import re 
import requests 
import json
# pd.set_option("display.max_rows", 100)
# from yachtcharter import yachtCharter
chart_key = f"oz-datablogs-something_random-asdfasdfadsf"

fillo = '/Users/josh_nicholas/github/live-corona-data-vaccine-page/omicron/oz.csv'

#%%

df = pd.read_csv(fillo)


# %%

zdf = df.copy()



for col in zdf.columns.tolist():
    if col not in ['week', 'total_sequences']:
        # print(col, zdf[col].sum())
        if zdf[col].sum() < 5:
            zdf.drop(columns=col)
        else:
            zdf[col] = (df[col]/zdf['total_sequences']) * 100

# for column in zdf.columns.tolist():
#     if col not in ['week', 'total_sequences']:
#         zdf.rename(columns={col:col.replace("cluster_counts.", '')}, inplace=True)

# callums = [x for x in ]

# print(zdf.columns)


# %%

fin = zdf.copy()
fin = fin[['week', 'cluster_counts.20A.EU2', 'cluster_counts.20A/S:439K', 'cluster_counts.20A/S:98F', 'cluster_counts.20B/S:732A', 'cluster_counts.20E (EU1)', 'cluster_counts.20H (Beta, V2)', 'cluster_counts.20I (Alpha, V1)', 'cluster_counts.20J (Gamma, V3)', 'cluster_counts.21A (Delta)', 'cluster_counts.21B (Kappa)', 'cluster_counts.21C (Epsilon)', 'cluster_counts.21D (Eta)', 'cluster_counts.21F (Iota)', 'cluster_counts.21G (Lambda)', 'cluster_counts.21H (Mu)', 'cluster_counts.21I (Delta)', 'cluster_counts.21J (Delta)', 'cluster_counts.21K (Omicron)', 'cluster_counts.S:677H.Robin1', 'cluster_counts.S:677P.Pelican']]

# callums = [x.replace("cluster_counts.", '') for x in fin.columns.tolist() if "cluster_counts." in x]
# callums = [re.search(r'\((.*?)\)',x).group(1) if "(" in x else x for x in callums]
# callums.insert(0, 'week')

# fin.columns = callums

# fin['Delta'] = 

# %%

## Load variants

r = requests.get('https://raw.githubusercontent.com/hodcroftlab/covariants/master/web/data/clusters.json')


# %%
vary = json.loads(r.text)

# for i in vary['clusters']:
# 	print(i)

df = pd.json_normalize(vary['clusters'])

p = df

print(p)
print(p.columns)



# fin['week'] = pd.to_datetime(fin['week'])
# fin = fin.sort_values(by='week', ascending=True)

# fin['week'] = fin['week'].dt.strftime('%Y-%m-%d')

# p = fin

# print(p)
# print(p.columns.tolist())

# # #%%

# fin.fillna(0, inplace=True)
# final = fin.to_dict(orient='records')

template = [
	{
	"title": "Covid variants in Australia",
	"subtitle": "Showing the proportion of Covid variants among cases that have been sequenced. Not all cases are sequenced and those that are may be unrepresentative.",
	"footnote": "",
	"source": "Covariants.org",
	"margin-left": "35",
	"margin-top": "30",
	"margin-bottom": "20",
	"margin-right": "10"
	}
]

# yachtCharter(template=template, 
# 			data=final,
# 			chartId=[{"type":"stackedarea"}],
# 			chartName=f"{chart_key}")

#%%
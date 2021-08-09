import requests
import scraperwiki
import lxml.html
import time

url = 'https://www.qld.gov.au/health/conditions/health-alerts/coronavirus-covid-19/current-status/statistics'

html = requests.get(url).content
parser = lxml.html.HTMLParser(encoding="utf-8")
dom = lxml.html.fromstring(html, parser=parser)

source_trs = dom.cssselect('#QLD_Cases_Sources_Of_Infection tr')
source_date = dom.cssselect('#QLD_Cases_Sources_Of_Infection caption')[0].text.replace("Data as at ","").replace(". Refer to ", "")
print(source_date)

source_data = []

for tr in source_trs:
	newRow = {}
	newRow["header"] = tr.cssselect('th')[0].text
	newRow["count"] = tr.cssselect('td')[0].text.replace(",","")
	newRow["date"] = source_date
	print(newRow)
	scraperwiki.sqlite.save(unique_keys=["header","date"], data=newRow, table_name="source")





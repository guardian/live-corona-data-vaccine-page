import simplejson as json
import boto3
import os


AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

if 'AWS_SESSION_TOKEN' in os.environ:
	AWS_SESSION = os.environ['AWS_SESSION_TOKEN']


def syncData(jsonObject,id):

	finalJson = json.dumps(jsonObject, indent=4)

	print("Connecting to S3")
	bucket = 'gdn-cdn'

	if 'AWS_SESSION_TOKEN' in os.environ:
		session = boto3.Session(
		aws_access_key_id=AWS_KEY,
		aws_secret_access_key=AWS_SECRET,
		aws_session_token = AWS_SESSION
		)
	else:
		session = boto3.Session(
		aws_access_key_id=AWS_KEY,
		aws_secret_access_key=AWS_SECRET,
		)

	s3 = session.resource('s3')

	key = "yacht-charter-data/{id}.json".format(id=id)
	object = s3.Object(bucket, key)
	object.put(Body=finalJson, CacheControl="max-age=30", ACL='public-read', ContentType="application/json")

	print("JSON is updated")

	print("data", "https://interactive.guim.co.uk/yacht-charter-data/{id}.json".format(id=id))
	print("chart", "https://interactive.guim.co.uk/embed/aus/2020/yacht-charter-v19/index.html?key={id}&location=yacht-charter-data".format(id=id))

def yachtCharter(template, data, chartName, trendline=[], dropdown = [], chartId=[{"type":"linechart"}], options=[{"colorScheme":""}],key=[], periods=[], labels=[]):

	jsonDictObject = {
		"sheets":{
			"template":template,
			"data":data,
			"labels":labels,
			"trendline":trendline,
			"key":key,
			"periods":periods,
			"labels":labels,
			"chartId":chartId,
			"options":options,
			"dropdown":dropdown
			}
	}

	#%% Sync

	syncData(jsonDictObject, chartName)

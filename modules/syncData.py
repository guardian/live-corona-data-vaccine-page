import boto3
import os

AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

def syncData(jsonObject,path,filename):

	print("Connecting to S3")
	bucket = 'gdn-cdn'

	session = boto3.Session(
	aws_access_key_id=AWS_KEY,
	aws_secret_access_key=AWS_SECRET,
	)
	s3 = session.resource('s3')

	key = "{path}/{filename}".format(path=path, filename=filename)
	object = s3.Object(bucket, key)
	object.put(Body=jsonObject, CacheControl="max-age=30", ACL='public-read', ContentType="application/json")

	print("JSON is updated")
	print("data", "https://interactive.guim.co.uk/{path}/{filename}".format(path=path, filename=filename))

import json
import boto3
import os

def lambda_handler(event, context):
	print(json.dumps(event))

	for record in event['Records']:
		if record['eventName'] in ['INSERT','MODIFY']:
			if 'RecordingURL' in record['dynamodb']['NewImage']:
				sns = boto3.client('sns')
				publish = sns.publish(
					TopicArn = os.environ['sns_topic_arn'],
					Subject = 'Connect call complete',
					Message = json.dumps(record['dynamodb']['NewImage'])
				)
				print(publish)
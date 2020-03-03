import json
import boto3
import os

def lambda_handler(event, context):
	print(json.dumps(event))

	for record in event['Records']:
		if record['eventName'] in ['INSERT','MODIFY']:
			if 'S3Path' in record['dynamodb']['NewImage']:

				s3 = boto3.client('s3')
				presigned_url = s3.generate_presigned_url(
					'get_object',
					Params = {
						'Bucket': record['dynamodb']['NewImage']['S3Path']['S'].split('/', 3)[2],
						'Key': record['dynamodb']['NewImage']['S3Path']['S'].split('/', 3)[3]
					},
					ExpiresIn = int(os.environ['url_expiry'])
				)
				record['dynamodb']['NewImage']['PresignedUrl'] = presigned_url
				sns = boto3.client('sns')
				publish = sns.publish(
					TopicArn = os.environ['sns_topic_arn'],
					Subject = 'Connect call complete',
					Message = json.dumps(record['dynamodb']['NewImage'], indent=4)
				)
				print(publish)
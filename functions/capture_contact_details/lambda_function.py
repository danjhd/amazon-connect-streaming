import json
import boto3
import os
import datetime

def lambda_handler(event, context):
	print(f'Event From Amazon Connect: {json.dumps(event)}')

	ddb = boto3.client('dynamodb')
	ddb.update_item(
		TableName = os.environ['table_name'],
		Key = {
			'ContactId': {'S': event['Details']['ContactData']['ContactId']}
		},
		ExpressionAttributeValues = {
			':var1': {'S': event['Details']['ContactData']['CustomerEndpoint']['Address']},
			':var2': {'S': datetime.datetime.utcnow().strftime('%Y-%m-%d')},
			':var3': {'S': datetime.datetime.now().strftime('%a %b %-d %Y %H:%M:%S')}
		},
		UpdateExpression = 'SET CustomerPhoneNumber = :var1, CallDate = :var2, CallTimestamp = :var3'
	)

	return {
		'lambdaResult': 'Success'
	}

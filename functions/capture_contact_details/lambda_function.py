import json
import datetime
import dateutil.tz
import boto3
import os

def lambda_handler(event, context):
	print(f'Event From Amazon Connect: {json.dumps(event)}')

	start_timestamp = datetime.datetime.fromtimestamp(int(event['Details']['ContactData']['MediaStreams']['Customer']['Audio']['StartTimestamp']) / 1000, tz = dateutil.tz.gettz(os.environ['TZ']))

	ddb = boto3.client('dynamodb')
	ddb.update_item(
		TableName = os.environ['table_name'],
		Key = {
			'ContactId': {'S': event['Details']['ContactData']['ContactId']}
		},
		ExpressionAttributeValues = {
			':var1': {'S': event['Details']['ContactData']['CustomerEndpoint']['Address']},
			':var2': {'S': start_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z')},
		},
		UpdateExpression = 'SET CustomerPhoneNumber = :var1, CallTimestamp = :var2'
	)

	return {
		'lambdaResult': 'Success'
	}

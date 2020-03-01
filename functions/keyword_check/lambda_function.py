import json
import boto3
import os

def lambda_handler(event, context):
	print(json.dumps(event))

	ssm = boto3.client('ssm')
	ddb = boto3.client('dynamodb')
	sns = boto3.client('sns')

	get_parameter = ssm.get_parameter(Name = os.environ['trigger_words_parameter'])
	connect_trigger_words = get_parameter['Parameter']['Value'].lower().split(',')

	for record in event['Records']:
		if record['eventName'] in ['INSERT','MODIFY']:
			if not record['dynamodb']['NewImage']['IsPartial']['BOOL']:
				matches = [k for k in connect_trigger_words if k in record['dynamodb']['NewImage']['Transcript']['S'].lower()]
				if len(matches) > 0:
					dbResults = ddb.query(
						TableName = os.environ['table_name'],
						KeyConditionExpression = 'ContactId = :varContactId',
						ExpressionAttributeValues = {
							':varContactId': {'S': record['dynamodb']['NewImage']['ContactId']['S']}
						}
					)
					dbResults['Items'][0]['MatchedTransscript'] = record['dynamodb']['NewImage']['Transcript']['S']
					dbResults['Items'][0]['MatchedWords'] = matches
					publish = sns.publish(
						TopicArn = os.environ['sns_topic_arn'],
						Subject = 'Connect key word alert',
						Message = json.dumps(dbResults['Items'][0])
					)
					print(publish)

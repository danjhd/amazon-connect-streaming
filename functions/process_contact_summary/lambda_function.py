import json
import boto3
import os
import urllib.parse

ddb = boto3.client('dynamodb')

def lambda_handler(event, context):
	print(f'Received event: {json.dumps(event)}')

	# Get the object from the event and show its content type
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

	# set the download URL
	recording_url = f'https://{bucket}.s3.amazonaws.com/{key}'

	# get file name ie: ContactID
	parsed = urllib.parse.urlparse(recording_url)
	file = os.path.basename(parsed.path)
	contact_id = file.split('_')[0]

	print(f'Received event for this contact ID: {contact_id}')

	contact_transcript_inbound = getTranscript(contact_id, os.environ['transcript_seg_table_name'])
	contact_transcript_outbound = getTranscript(contact_id, os.environ['transcript_seg_to_customer_table_name'])

	ddb.update_item(
		TableName = os.environ['contact_table_name'],
		Key = {
			'ContactId': {'S': contact_id}
		},
		ExpressionAttributeValues = {
			':var1': {'S': contact_transcript_inbound},
			':var2': {'S': contact_transcript_outbound},
			':var3': {'S': recording_url}
		},
		UpdateExpression = 'SET ContactTranscriptFromCustomer = :var1, ContactTranscriptToCustomer = :var2, RecordingURL = :var3'
	)

def getTranscript(contact_id, table_name):
	dbResults = ddb.query(
		TableName = table_name,
		KeyConditionExpression = 'ContactId = :varContactId',
		ExpressionAttributeValues = {
			':varContactId': {'S': contact_id}
		}
	)

	transcript = ' '.join([r['Transcript']['S'] for r in dbResults['Items'] if 'Transcript' in r])
	transcript = transcript if transcript != '' else 'Transcript not available for this call'

	print(f'table ({table_name}) has the transcript: {transcript}')

	return transcript

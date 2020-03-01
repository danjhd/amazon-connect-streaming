import json
import boto3
import os

def lambda_handler(event, context):
	print(f'Received event from Amazon Connect {json.dumps(event)}')

	payload = {
		'streamARN': event['Details']['ContactData']['MediaStreams']['Customer']['Audio']['StreamARN'],
		'startFragmentNum': event['Details']['ContactData']['MediaStreams']['Customer']['Audio']['StartFragmentNumber'],
		'connectContactId': event['Details']['ContactData']['ContactId'],
		'transcriptionEnabled': event['Details']['ContactData']['Attributes']['transcribeCall'].lower() == 'true',
		'saveCallRecording': event['Details']['ContactData']['Attributes']['saveCallRecording'].lower() == 'true',
		'languageCode': event['Details']['ContactData']['Attributes']['languageCode']
	}
	print(f'Trigger event passed to transcriberFunction: {json.dumps(payload)}')

	lam = boto3.client('lambda')
	lam.invoke(
		FunctionName = os.environ['transcribe_function'],
		InvocationType = 'Event',
		Payload = json.dumps(payload),
	)

	return {
		'lambdaResult': 'Success'
	}

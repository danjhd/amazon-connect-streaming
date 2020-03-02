import cfnresponse
import json
import boto3
import os

def lambda_handler(event, context):

	try:
		if event['RequestType'] in ['Create', 'Update']:
			contact_flow = json.loads(open('streaming_flow.json', 'r').read())
			for module in contact_flow['modules']:
				if module['type'] == 'InvokeExternalResource':
					for parameter in module['parameters']:
						if parameter['name'] == 'FunctionArn':
							parameter['value'] = os.environ[f"{parameter['value']}Arn"]
			s3 = boto3.client('s3')
			put_object = s3.put_object(
				Bucket = os.environ['s3_bucket'],
				Key = 'streaming_flow.json',
				Body = json.dumps(contact_flow, indent=4)
			)
			print(put_object)
			s3 = boto3.resource('s3')
			s3.meta.client.upload_file('silent_hold_queue.json', os.environ['s3_bucket'], 'silent_hold_queue.json')
			s3.meta.client.upload_file('Silent.wav', os.environ['s3_bucket'], 'Silent.wav')
			cfnresponse.send(event, context, cfnresponse.SUCCESS, None, context.aws_request_id)
		else:
			s3 = boto3.client('s3')
			for key in ['streaming_flow.json', 'silent_hold_queue.json', 'Silent.wav']:
				delete_object = s3.delete_object(
						Bucket = os.environ['s3_bucket'],
						Key = key,
				)
				print(delete_object)
			cfnresponse.send(event, context, cfnresponse.SUCCESS, None)
	except Exception as ex:
		cfnresponse.send(event, context, cfnresponse.FAILED, None, context.aws_request_id)
		raise ex
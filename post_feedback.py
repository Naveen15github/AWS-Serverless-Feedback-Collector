import json, boto3, uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FeedbackTable')

def handler(event, context):
    body = json.loads(event.get('body', '{}'))
    if not body.get('name') or not body.get('message'):
        return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'Name and message are required'})}
    item = {'id': str(uuid.uuid4()), 'name': body['name'], 'email': body.get('email', ''), 'message': body['message'], 'timestamp': datetime.utcnow().isoformat()}
    table.put_item(Item=item)
    return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': 'Feedback saved!'})}

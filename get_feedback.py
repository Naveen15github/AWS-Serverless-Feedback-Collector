import json, boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FeedbackTable')

def handler(event, context):
    result = table.scan(Limit=50)
    items = sorted(result.get('Items', []), key=lambda x: x.get('timestamp',''), reverse=True)
    return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps(items)}

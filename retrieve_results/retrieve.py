import json
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('QueryResults')  # Ensure this matches your actual table name

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        query_params = event.get('queryStringParameters', {})
        if not query_params:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No query parameters provided'})
            }

        query_name = query_params.get('query_name')
        date_range = query_params.get('date_range', 'current')

        if not query_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'query_name is required'})
            }

        end_date = datetime.now().date()
        if date_range == 'past7':
            start_date = end_date - timedelta(days=7)
        elif date_range == 'past14':
            start_date = end_date - timedelta(days=14)
        elif date_range == 'past30':
            start_date = end_date - timedelta(days=30)
        else:  # current
            start_date = end_date

        logger.info(f"Querying for {query_name} from {start_date} to {end_date}")

        response = table.query(
            KeyConditionExpression=Key('query_name').eq(query_name) & 
                                   Key('date').between(start_date.isoformat(), end_date.isoformat())
        )

        logger.info(f"Query response: {json.dumps(response, cls=DecimalEncoder)}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
            'body': json.dumps(response['Items'], cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
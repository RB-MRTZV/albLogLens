import json
import boto3
import os
import asyncio
from datetime import datetime, timedelta


athena = boto3.client('athena')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('QueryResults')

#Define Athena database and table
database =  os.environ['Athena_DB_Name']
table_name =  os.environ['Athena_Table_Name']
period =  os.environ['Query_Period_In_Days']


# Define the queries
queries = {
    'client_ip': f"""
        SELECT client_ip, COUNT(*) AS RequestCount 
        FROM {database}.{table_name} 
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d') 
        AND date_format(current_date, '%Y/%m/%d')
        GROUP BY client_ip 
        ORDER BY RequestCount DESC 
        LIMIT 10
    """,
    'most_requested': f"""
        SELECT request_url, COUNT(*) AS RequestCount 
        FROM {database}.{table_name} 
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d') 
        AND date_format(current_date, '%Y/%m/%d') 
        GROUP BY request_url 
        ORDER BY RequestCount DESC  
        LIMIT 10
    """,
    'status_code': f"""
        SELECT elb_status_code, COUNT(*) AS RequestCount 
        FROM {database}.{table_name} 
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d') 
        AND date_format(current_date, '%Y/%m/%d')
        GROUP BY elb_status_code 
        ORDER BY RequestCount DESC  
        LIMIT 10
    """,
    'most_4xx_ips': f"""
        SELECT client_ip, COUNT(*) AS error_count 
        FROM {database}.{table_name}
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d') 
        AND date_format(current_date, '%Y/%m/%d')
        AND elb_status_code >= 400 
        GROUP BY client_ip 
        ORDER BY error_count DESC 
        LIMIT 10
    """,
    'high_latency': f"""
        SELECT client_ip, request_url, target_processing_time 
        FROM {database}.{table_name}
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d') 
        AND date_format(current_date, '%Y/%m/%d')
        AND target_processing_time > 5
        ORDER BY target_processing_time DESC 
        LIMIT 10
    """,
    'ssl_usage': f"""
        SELECT ssl_protocol, COUNT(*) AS usage_count 
        FROM {database}.{table_name}
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d')
        AND date_format(current_date, '%Y/%m/%d') 
        AND ssl_protocol IS NOT NULL 
        GROUP BY ssl_protocol 
        ORDER BY usage_count DESC
    """,
    'user_agent': f"""
        SELECT user_agent, COUNT(*) AS request_count 
        FROM {database}.{table_name}
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d')
        AND date_format(current_date, '%Y/%m/%d') 
        GROUP BY user_agent 
        ORDER BY request_count DESC 
        LIMIT 10
    """,
    'http_distribution': f"""
        SELECT request_verb, COUNT(*) AS method_count 
        FROM {database}.{table_name}
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d')
        AND date_format(current_date, '%Y/%m/%d') 
        GROUP BY request_verb 
        ORDER BY method_count DESC
    """,
    'target_average_responsetime': f"""
        SELECT target_group_arn, AVG(target_processing_time) AS avg_response_time, 
               MAX(target_processing_time) AS max_response_time 
        FROM {database}.{table_name}
        WHERE day BETWEEN date_format(date_add('day', -{period}, current_date), '%Y/%m/%d')
        AND date_format(current_date, '%Y/%m/%d') 
        GROUP BY target_group_arn 
        ORDER BY avg_response_time DESC
    """
}

bucket_name = os.environ['OUTPUT_BUCKET']
output_bucket = f's3://{bucket_name}'

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


async def execute_query(query):
    query_response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database},
        ResultConfiguration={'OutputLocation': output_bucket}
    )
    query_execution_id = query_response['QueryExecutionId']
    
    while True:
        query_status = athena.get_query_execution(QueryExecutionId=query_execution_id)
        state = query_status['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        await asyncio.sleep(1)
    
    if state == 'SUCCEEDED':
        results = athena.get_query_results(QueryExecutionId=query_execution_id)
        return results
    else:
        return None


def store_results(query_name, results):
    date = datetime.now().strftime('%Y-%m-%d')
    item = {
        'query_name': query_name,
        'date': date,
        'results': results,
        'timestamp': int(datetime.now().timestamp())
    }
    table.put_item(Item=item)


def lambda_handler(event, context):
    async def run_queries():
        results = {}
        for query_name, query in queries.items():
            query_results = await execute_query(query)
            if query_results:
                processed_results = []
                for row in query_results['ResultSet']['Rows'][1:]:  # Skip the header row
                    processed_results.append({
                        column['Name']: row['Data'][i]['VarCharValue'] 
                        for i, column in enumerate(query_results['ResultSet']['ResultSetMetadata']['ColumnInfo'])
                    })
                results[query_name] = processed_results
                store_results(query_name, processed_results)
            else:
                results[query_name] = "Query failed or was cancelled"
        return results

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_queries())

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(results, cls=DecimalEncoder)  # Use your existing serialization method
    }
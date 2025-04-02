import json
import boto3
from transcribe import transcribe_with_whisper
from generate_response import prompt
from query_constructor import construct_query

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YourDynamoDBTable')

def retrieve_db(customer_query):
    expression, expression_values = construct_query(customer_query)

    try:
        response = table.scan(
            FilterExpression=expression,
            ExpressionAttributeValues=expression_values
        )
        
        db_return = response.get('Items', [])
        
        if db_return:
            # Format room information into a string for the LLM to process
            db_context = "\n".join([f"Room ID: {room['RoomID']}, Price: ${room['Price']}, Availability: {room['Availability']}" for room in db_return])

            response = prompt(customer_query, db_context)

            return {
                'statusCode': 200,
                'body': {
                    'gpt_response': response.choices[0].text.strip()
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': {"message": "No rooms found matching the query"}
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {"message": f"Error retrieving data from DynamoDB: {str(e)}"}
        }


def lambda_handler(event, context):
    customer_query = event['cutomer_query']

    db_response = retrieve_db(customer_query)

    return {"statusCode": 200, "body": json.dumps("Hello from Github!")}

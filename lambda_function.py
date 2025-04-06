import json
import boto3
from transcribe import transcribe_with_whisper
from generate_response import prompt
from query_constructor import construct_query

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("YourDynamoDBTable")


def retrieve_db(customer_query):
    expression, expression_values = construct_query(customer_query)

    try:
        response = table.scan(
            FilterExpression=expression, ExpressionAttributeValues=expression_values
        )

        db_return = response.get("Items", [])

        if db_return:
            db_context = "\n".join(
                [
                    f"Room ID: {room['RoomID']}, Price: ${room['Price']}, Availability: {room['Availability']}"
                    for room in db_return
                ]
            )

            response = prompt(customer_query, db_context)

            return {
                "statusCode": 200,
                "body": {"gpt_response": response.choices[0].text.strip()},
            }
        else:
            return {
                "statusCode": 404,
                "body": {"message": "No rooms found matching the query"},
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": f"Error retrieving data from DynamoDB: {str(e)}"},
        }


def lambda_handler(event, context):
    customer_query = (
        event["body"].split("SpeechResult=")[1].split("&")[0].replace("+", " ")
    )

    db_response = retrieve_db(customer_query)

    response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>{db_response}</Say>
    </Response>"""

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/xml"},
        "body": response_xml,
    }

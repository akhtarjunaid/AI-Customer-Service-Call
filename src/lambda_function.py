from urllib.parse import parse_qs
import boto3
from src.transcribe import transcribe_with_whisper
from generate_response import prompt
from query_constructor import construct_query

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("hotel-information")


def retrieve_db(customer_query, session_id):
    expression, expression_values = construct_query(customer_query)

    if not expression:
        return {
            "statusCode": 400,
            "body": {
                "message": "Sorry, I couldn't find enough details in your request. \
                Can you tell me the room location, type, price range, or any amenities \
                you're looking for?"
            },
        }

    kwargs = {
        "FilterExpression": expression,
        "ExpressionAttributeValues": expression_values,
    }

    try:
        response = table.scan(**kwargs)

        db_return = response.get("Items", [])

        if db_return:
            db_context = "\n".join(
                [
                    f"Room ID: {room.get('roomid')}, Price: ${room.get('room_price')}, "
                    f"Location: {room.get('room_location')}, Type: {room.get('room_type')}, "
                    f"Booked Dates: {', '.join(room.get('days_booked', []))}"
                    for room in db_return
                ]
            )

            response = prompt(customer_query, db_context, session_id)

            return {
                "statusCode": 200,
                "body": {"gpt_response": response.strip()},
            }
        else:
            return {
                "statusCode": 404,
                "body": {"message": "No rooms found matching the query"},
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {
                "message": f"Error retrieving data from DynamoDB: {str(e)}. \
                    Expression: {str(expression)}. Expression Values: {str(expression_values)}"
            },
        }


def lambda_handler(event, context):
    parsed_body = parse_qs(event["body"])
    session_id = parsed_body.get("CallSid", ["anonymous"])[0]
    customer_query = parsed_body.get("SpeechResult", [""])[0]

    if "SpeechResult" not in parsed_body:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/xml"},
            "body": f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Gather input="speech" action="https://g9j6r5ypl5.execute-api.us-east-2.amazonaws.com/test/chat" method="POST" timeout="5" speechTime="auto">
                    <Say>Thank you for calling, how can I help you today?</Say>
                </Gather>
                <Say>Sorry, I didn't catch that. Goodbye!</Say>
            </Response>""",
        }

    db_response = retrieve_db(customer_query, session_id)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/xml"},
        "body": f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say>{db_response}</Say>
            <Redirect method="POST">/chat</Redirect>
        </Response>""",
    }

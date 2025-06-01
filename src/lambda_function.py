from urllib.parse import parse_qs
import boto3
from generate_response import prompt
from query_constructor import construct_query

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("hotel-information")


def retrieve_db(customer_query, session_id):
    table_query = table.scan()
    rooms = table_query["Items"]

    context_lines = []
    for r in rooms:
        context_lines.append(
            f"Room {r['room_number']} is a {r['room_type']} in {r['room_location']} "
            f"for ${r['price']} per night. Booked days: {', '.join(r.get('days_booked', []))}"
        )
    context = "\n".join(context_lines)

    response = prompt(customer_query, context, session_id)

    return response


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
                <Gather input="speech" language="en-US" action="https://g9j6r5ypl5.execute-api.us-east-2.amazonaws.com/test/chat" method="POST" timeout="10" speechTimeout="auto">
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
            <Gather input="speech" language="en-US" action="https://g9j6r5ypl5.execute-api.us-east-2.amazonaws.com/test/chat" method="POST" timeout="7" speechTimeout="auto">
                <Say>Do you have any further questions?</Say>
            </Gather>
            <Say>Sorry, I didn't catch that. Goodbye!</Say>
        </Response>""",
    }

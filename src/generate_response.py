import os
import time
from openai import OpenAI
import boto3

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("hotel-customer-service-chat-memory")


def get_conversation(session_id):
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("session_id").eq(
            session_id
        ),
        ScanIndexForward=True,
    )
    messages = [
        {"role": item["role"], "content": item["content"]} for item in response["Items"]
    ]
    return messages


def store_message(session_id, role, content):
    timestamp = str(int(time.time()))
    table.put_item(
        Item={
            "session_id": session_id,
            "timestamp": timestamp,
            "role": role,
            "content": content,
        }
    )


def prompt(customer_query, db_context, session_id):
    messages = get_conversation(session_id)

    messages.append({"role": "user", "content": customer_query})
    store_message(session_id, "user", customer_query)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"You are a helpful assistant who is helping a customer with inquires \
                about a hotel. Here is the information about all rooms: {db_context} \
                The customer said this: {customer_query}. \
                Please answer the customer query based on the room information. \
                Keep your response friendly but as to-the-point and concise as possible.",
            },
        ],
        temperature=0.3,
    )
    bot_response = response.choices[0].message.content.strip()

    store_message(session_id, "assistant", bot_response)

    return bot_response

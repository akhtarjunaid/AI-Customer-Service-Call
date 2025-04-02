import json
import os

openai_api_key = os.getenv("OPENAI_API_KEY")


def lambda_handler(event, context):
    print(f"Using OpenAI API Key: {openai_api_key[:5]}...")
    return {"statusCode": 200, "body": json.dumps("Hello from Github!")}

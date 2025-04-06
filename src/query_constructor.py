import re
import json
import os
from openai import OpenAI


openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

locations = ["New York", "Tokyo"]
room_types = ["king bed", "queen bed", "suite", "single room"]
amenities = ["Wi-Fi", "pool", "free breakfast", "parking", "gym"]


def extract_location(query):
    for location in locations:
        if location.lower() in query.lower():
            return location
    return None


def extract_price_range(query):
    match = re.search(r"\$(\d+)\s*-\s*\$(\d+)", query)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None


def extract_room_type(query):
    for room_type in room_types:
        if room_type.lower() in query.lower():
            return room_type
    return None


def extract_amenities(query):
    found_amenities = []
    for amenity in amenities:
        if amenity.lower() in query.lower():
            found_amenities.append(amenity)
    return found_amenities


def extract_filters_with_llm(user_query):
    prompt = f"""
    You are helping extract filter conditions for a DynamoDB hotel booking database. \
    The table has these columns:

    - roomid (string)
    - days_booked (set of strings)
    - room_price (number)
    - room_location (string)
    - room_number (number)
    - room_type (string)

    Given this user query: "{user_query}"

    Return a JSON object with any relevant filters the user is requesting. \
    Each key should be one of the column names. "You can include numeric ranges using \
    `{{ \"min\": val, \"max\": val }}`". If a field is not mentioned, omit it.

    Return a **raw JSON object only**, like this:
    {{
        "roomid": 1,
        "room_type": "king bed",
        "room_location": "New York",
        "room_price": {{
            "max": 250
        }}
    }}

    No explanation, no markdown, no code blocks — only return the JSON itself. 
    If you are not sure how to respond, still format the response in JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    filters = json.loads(response.choices[0].message.content)

    return filters


def construct_query(customer_query):
    expression_parts = []
    expression_values = {}

    filters = extract_filters_with_llm(customer_query)

    for key, value in filters.items():
        if isinstance(value, dict) and "min" in value and "max" in value:
            expression_parts.append(f"{key} BETWEEN :min_{key} AND :max_{key}")
            expression_values[f":min_{key}"] = value["min"]
            expression_values[f":max_{key}"] = value["max"]
        elif isinstance(value, list):
            for i, item in enumerate(value):
                tag = f":{key}{i}"
                expression_parts.append(f"contains({key}, {tag})")
                expression_values[tag] = item
        else:
            expression_parts.append(f"{key} = :{key}")
            expression_values[f":{key}"] = value

    expression = " AND ".join(expression_parts) if expression_parts else None

    return expression, expression_values

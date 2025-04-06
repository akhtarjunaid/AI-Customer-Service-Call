from openai import OpenAI
import os

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


def prompt(customer_query, db_context):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Customer asked: {customer_query} \
                    \nHere are some room options:\n{db_context} \
                    \nPlease answer the customer query based on the room information.",
            },
        ],
    )

    return response.choices[0].message.content

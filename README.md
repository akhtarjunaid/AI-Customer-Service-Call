# Serverless AI Phone Assistant

This project is a serverless, real-time AI phone assistant that leverages AWS services, Docker, and Twilio to create an intelligent voice-based interface to handle hotel inquiries.

---

## Tech Stack

- **AWS Lambda**: Executes the AI logic in a serverless manner.
- **Amazon API Gateway**: Acts as the interface for Twilio to send real-time audio to AWS.
- **Amazon ECR**: Hosts the Docker image for Lambda.
- **Amazon DynamoDB**: Stores conversation logs and context.
- **Docker**: Used to package the Python Lambda function.
- **Twilio**: Handles the voice call and streams audio in real-time.

---

## Features

- AI responses generated using `gpt-4o-mini`
- Low-latency response pipeline
- Scalable, serverless architecture
- Call logging and context persistence with DynamoDB

---

## Setup Instructions

First, make sure you have the following:

- Docker installed
- An AWS account with Lambda, API Gateway, DynamoDB, and ECR
- AWS CLI installed
- Twilio account with a voice-capable phone number
- Python 3.12

Next, create the docker image and push to ECR:

```
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com
docker build -t YOUR-DOCKER-IMAGE .
docker tag ai-assistant:latest YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/YOUR-DOCKER-IMAGE:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/YOUR-DOCKER-IMAGE:latest
```
To run the docker image, create a container Lambda function and load the image you pushed earlier. 

We will also need to create two DynamoDB tables. One will be for storing hotel information, the other for storing chat bot interaction history. 

Finally, we need to connect Twilio to our lambda function. To do so, create a new resource in AWS API Gateway with a POST method.

---

## Thats it! 

You can now test your client by calling your Twilio number. 

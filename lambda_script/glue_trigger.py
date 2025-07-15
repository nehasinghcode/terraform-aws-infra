import boto3
import os
import json

def lambda_handler(event, context):
    glue_client = boto3.client('glue')
    job_name = os.environ['GLUE_JOB_NAME']

    print("Received event:")
    print(json.dumps(event))

    try:
        # Optional: extract S3 bucket & object key info from event
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        print(f"Triggering Glue job for file: s3://{bucket}/{key}")

        # Start Glue job
        response = glue_client.start_job_run(
            JobName=job_name,
            Arguments={
                "--SOURCE_BUCKET": bucket,
                "--SOURCE_KEY": key
            }
        )

        print(f"Glue job started: JobRunId = {response['JobRunId']}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Glue job started: {response['JobRunId']}")
        }

    except Exception as e:
        print("Error starting Glue job:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }

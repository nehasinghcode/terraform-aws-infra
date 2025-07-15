import boto3
import os

def lambda_handler(event, context):
    glue = boto3.client('glue')
    
    try:
        # Extract bucket and object key from the S3 event
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        raw_s3_path = f"s3://{bucket}/{key}"
        print(f"File uploaded to: {raw_s3_path}")
    except Exception as e:
        print("Error extracting bucket/key:", str(e))
        raise

    # Get Glue Job name from environment variable
    glue_job_name = os.environ.get("GLUE_JOB_NAME")
    if not glue_job_name:
        raise ValueError("GLUE_JOB_NAME environment variable not set")

    try:
        # Start Glue job with S3 path as an argument
        response = glue.start_job_run(
            JobName=glue_job_name,
            Arguments={
                "--raw_s3_path": raw_s3_path
            }
        )
        print(f"Glue job started: {response['JobRunId']}")
        return {
            "statusCode": 200,
            "body": f"Started Glue job {glue_job_name} for file {raw_s3_path}"
        }

    except Exception as e:
        print("Error starting Glue job:", str(e))
        raise

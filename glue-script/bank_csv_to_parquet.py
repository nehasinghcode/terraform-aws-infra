import sys
import boto3
import os
from awsglue.context import GlueContext
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, when
from awsglue.dynamicframe import DynamicFrame

# Get parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'raw_s3_path'])
job_name = args['JOB_NAME']
raw_path = args['raw_s3_path']
output_path = "s3://finco-dev-curated-csv-data-us-east-1-001/curated_data/"
manifest_path = "s3://finco-dev-curated-csv-data-us-east-1-001/processed_files/"

sns_topic_arn = "arn:aws:sns:us-east-1:879468317396:glue-job-notifications"  # ← Replace YOUR_ACCOUNT_ID

# Initialize boto3 clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

def send_notification(subject, message):
    sns.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

try:
    print(f"Input path: {raw_path}")
    print(f"Output path: {output_path}")
    print(f"Manifest path: {manifest_path}")

    # Parse input file key
    filename = raw_path.split("/")[-1]
    manifest_key = f"{manifest_path}{filename}.manifest"
    bucket = manifest_path.replace("s3://", "").split("/")[0]
    manifest_obj_key = "/".join(manifest_key.split("/")[1:])

    # Check if file was already processed
    try:
        s3.head_object(Bucket=bucket, Key=manifest_obj_key)
        print(f"File {filename} already processed. Skipping.")
        send_notification(
            subject=f"Glue Job '{job_name}' Skipped",
            message=f"The file '{filename}' was already processed and skipped."
        )
        sys.exit(0)
    except:
        print(f"File {filename} is new. Proceeding...")

    # Spark & Glue context
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session

    # Read CSV with header and semicolon delimiter
    df = spark.read.option("header", True).option("sep", ";").csv(raw_path)
    print("Data read successfully")
    df.printSchema()

    # Basic transformations
    df = df.withColumn("default", when(col("default") == "yes", 1).otherwise(0)) \
           .withColumn("housing", when(col("housing") == "yes", 1).otherwise(0)) \
           .withColumn("loan", when(col("loan") == "yes", 1).otherwise(0))

    # Example aggregation
    agg_df = df.groupBy("month").agg({"balance": "avg"}).withColumnRenamed("avg(balance)", "avg_balance")
    agg_df.show()

    # Convert to DynamicFrame
    dyf = DynamicFrame.fromDF(df, glueContext, "dyf")

    # Write to Parquet in partitioned structure
    glueContext.write_dynamic_frame.from_options(
        frame=dyf,
        connection_type="s3",
        format="parquet",
        connection_options={
            "path": output_path,
            "partitionKeys": ["month"],
            "mode": "overwrite"
        }
    )
    print("Write completed")

    # Mark as processed by uploading empty manifest file
    s3.put_object(Bucket=bucket, Key=manifest_obj_key, Body='')
    print(f"Manifest file created for {filename}")

    # Send success notification
    print(">>> Sending success notification")
    send_notification(
        subject=f"Glue Job '{job_name}' Success",
        message=f"The file '{filename}' was processed successfully and output was written to S3."
    )
    print(">>> Sending success notification completed")

except Exception as e:
    error_msg = f"Glue Job '{job_name}' Failed.\nError: {str(e)}"
    print(error_msg)
    send_notification(
        subject=f"Glue Job '{job_name}' Failed",
        message=error_msg
    )
    raise

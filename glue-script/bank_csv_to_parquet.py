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
raw_path = args['raw_s3_path']
output_path = "s3://finco-dev-curated-csv-data-us-east-1-001/curated_data/"
manifest_path = "s3://finco-dev-curated-csv-data-us-east-1-001/processed_files/"

print(f"Input path: {raw_path}")
print(f"Output path: {output_path}")
print(f"Manifest path: {manifest_path}")

# Parse input file key
filename = raw_path.split("/")[-1]
manifest_key = f"{manifest_path}{filename}.manifest"

# Check if file was already processed
s3 = boto3.client('s3')
bucket = manifest_path.replace("s3://", "").split("/")[0]
manifest_obj_key = "/".join(manifest_key.split("/")[1:])

try:
    s3.head_object(Bucket=bucket, Key=manifest_obj_key)
    print(f"File {filename} already processed. Skipping.")
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

# Add transformation: average balance by month (optional example)
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

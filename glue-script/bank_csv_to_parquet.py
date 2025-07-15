# glue-script/bank_csv_to_parquet.py

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext

# Script generated for job bank_csv_to_parquet_job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = glueContext.create_job(args['JOB_NAME'])

# Read raw CSV from S3
raw_data = glueContext.create_dynamic_frame.from_options(
    format_options={"withHeader": True},
    connection_type="s3",
    format="csv",
    connection_options={"paths": ["s3://finco-dev-raw-csv-data-us-east-1-001/bank.csv"]},
    transformation_ctx="raw_data"
)

# Write as Parquet to curated bucket
glueContext.write_dynamic_frame.from_options(
    frame=raw_data,
    connection_type="s3",
    format="parquet",
    connection_options={"path": "s3://finco-dev-curated-csv-data-us-east-1-001/processed/"},
    transformation_ctx="output"
)

job.commit()

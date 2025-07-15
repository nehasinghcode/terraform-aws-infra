import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, avg, count
from pyspark.sql import SparkSession

# Initialize contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Get parameters from Lambda event via Glue Job arguments
args = getResolvedOptions(sys.argv, ['RAW_S3_PATH'])

raw_s3_path = args['RAW_S3_PATH']

# Read CSV from S3 with proper options
df = spark.read.option("header", "true") \
               .option("inferSchema", "true") \
               .option("quote", "\"") \
               .option("multiLine", "true") \
               .option("escape", "\"") \
               .csv(raw_s3_path)

# Strip and lowercase column names
df = df.toDF(*[c.strip().lower() for c in df.columns])

# Print columns for debugging
print("Sanitized Columns:", df.columns)

# Filter records where age > 30 and balance > 0
df_filtered = df.filter((col('age') > 30) & (col('balance') > 0))

# Perform aggregation: average balance and count by job and marital
df_agg = df_filtered.groupBy('job', 'marital') \
                    .agg(
                        avg('balance').alias('avg_balance'),
                        count('*').alias('record_count')
                    )

# Write to Parquet partitioned by job and marital
output_path = "s3://finco-dev-curated-csv-data-us-east-1-001/cleaned_data/"
df_agg.write \
     .mode("overwrite") \
     .partitionBy("job", "marital") \
     .format("parquet") \
     .save(output_path)

# Register output in Glue Catalog
glueContext.purge_table("bank_marketing_curated", "bank_data_cleaned", options={"retention": 0})
glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [output_path]},
    format="parquet"
).toDF().write \
 .format("parquet") \
 .mode("overwrite") \
 .option("path", output_path) \
 .option("partitionKeys", ["job", "marital"]) \
 .saveAsTable("bank_marketing_curated.bank_data_cleaned")
